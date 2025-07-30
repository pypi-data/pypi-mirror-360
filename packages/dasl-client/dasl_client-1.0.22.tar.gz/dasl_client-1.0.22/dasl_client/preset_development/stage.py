from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import *
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col, lit
from dasl_client.preset_development.errors import *

FieldSpec = Dict[str, Any]


class Node:
    """
    Represents a node in a tree structure. This is used to figure out STRUCT types
    and ensure proper subSTRUCT reconciliation at data output.
    """

    pass


class Branch(Node):
    """
    Represents a branch in a tree structure.
    """

    def __init__(self, children: Dict[str, Node] = None):
        self._children: Dict[str, Node] = children if children is not None else {}


class Leaf(Node):
    """
    Represents a leaf node in a tree structure.
    """

    def __init__(self, field: FieldSpec):
        self._field = field


class Stage:
    """
    Stage represents a single stage's table and contains all logic required to correctly perform
    operations as defined in the table's field specifications, utility functions, filters, and more.

    To operate, it takes in a DataFrame and returns a new DataFrame with the defined operations
    applied. The resulting DataFrame can be used in subsequent stages if required.
    """

    __op_list = ["assert", "literal", "from", "alias", "expr", "join"]

    def __init__(self, spark: SparkSession, stage: str, table: Dict[str, any]):
        """
        Initializes a Stage object that encapsulates all operations required for a single
        table within a stage.

        Instance Attributes:
            stage (str): The medallion layer stage name.
            name (str): The name of the table.
            filter (str): The filter applied before operations.
            postFilter (str): The filter applied after operations.
            utils (Dict[str, Any]): Utility operations to perform on the DataFrame.
            input (str): The name of the prior stage's table to use as input.
            fields (List[Dict[str, str]]): Field specification operations to apply.
            assertions (List[Dict[str, List[str]]]): Assertions to apply after operations.
        """
        self._spark = spark
        self._stage = stage
        self._name = table.get("name", "")
        self._filter = table.get("filter", "")
        self._postFilter = table.get("postFilter", "")
        self._utils = table.get("utils", {})
        self._input = table.get("input", None)

        fields = (
            [{"name": "dasl_id", "from": "dasl_id"}] + table.get("fields", [])
            if self._stage != "temp_fields"
            else table.get("fields", [])
        )
        self._fields = [
            f for f in fields if (f.get("name", None) and not f.get("assert", None))
        ]
        self._assertions = [f for f in fields if f.get("assert", None)]

        names = []
        for field in self._fields:
            if not (name := field.get("name", None)):
                if not field.get("assert", None):  # Can't walrus em all :/
                    raise MissingFieldNameError(self._stage, self._name)
            if name in names:
                raise DuplicateFieldNameError(self._stage, self._name, name)
            names += [name]

            missing_op_count = [
                spec for spec in [field.get(op, None) for op in self.__op_list]
            ].count(None)
            if (missing_op_count == len(self.__op_list)) or (
                len(self.__op_list) - missing_op_count > 1
            ):
                raise MalformedFieldError(
                    self._stage, self._name, field.get("name", None)
                )

    def _referenced_columns(self) -> List[str]:
        """
        Get a list of columns referenced in the table's field specifications.

        Returns:
            A list of referenced columns.
        """
        return [field.get("from") for field in self._fields if field.get("from", None)]

    def _column_names(self) -> List[str]:
        """
        Returns a list of column names referenced in the table's field specifications.

        Returns:
            A list of columns names.
        """
        return [field.get("name") for field in self._fields]

    def _omitted_columns(self) -> List[str]:
        """
        Get omitted columns from the preserve utility function object.

        Returns:
            A list of omitted columns.
        """
        preserve = self._utils.get("unreferencedColumns", None)
        return [] if not preserve else preserve.get("omitColumns", [])

    def _duplicate_prefix(self) -> str:
        """
        Get the prefix to use for duplicate fields. If not provided, returns a default.

        Returns:
            The duplicate prefix string.
        """
        preserve = self._utils.get("unreferencedColumns", None)
        return "d_" if not preserve else preserve.get("duplicatePrefix", "d_")

    def json_extract_boilerplate(
        self, df: DataFrame, source: str, omit_fields: List[str], duplicate_prefix: str
    ) -> Tuple[StructType, List[str]]:
        """
        Processes the common schema and column information needed from a target JSON
        containing column.

        Returns:
            The schema and columns extracted from the target JSON.
        """
        target_col = source
        existing_columns = df.columns
        if target_col not in existing_columns:
            raise ReferencedColumnMissingError("jsonExtract", target_col)
        schema = self._spark.sql(
            f"SELECT schema_of_json_agg({self.auto_backtick(target_col)}) AS sc FROM {{df}}",
            df=df,
        ).collect()[0][0]
        extract_df = self._spark.createDataFrame(data=[], schema=schema)
        columns = extract_df.columns
        columns = [
            self.auto_backtick(f"extract.{col}") + f" AS {self.auto_backtick(col)}"
            for col in columns
            if col not in omit_fields and col not in existing_columns
        ]
        columns += [
            self.auto_backtick(f"extract.{col}")
            + f" AS {self.auto_backtick(duplicate_prefix + col)}"
            for col in columns
            if col not in omit_fields and col in existing_columns
        ]
        return (schema, columns)

    def json_extract(
        self, df: DataFrame, schema: str, columns: List[str], target_col: str
    ) -> DataFrame:
        """
        Prefroms JSON extraction to new fields in the DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        return (
            df.selectExpr(
                "*",
                f"from_json({self.auto_backtick(target_col)}, '{schema}') AS extract",
            )
            .selectExpr("*", *columns)
            .drop("extract")
        )

    def json_extract_embed_column(
        self,
        df: DataFrame,
        schema: str,
        omit_fields: List[str],
        target_col: str,
        name: str,
    ) -> DataFrame:
        """
        Performs JSON extraction embedding new JSON fields to a single new field in
        the DataFrame. (Serialized as JSON.)

        Returns:
            A DataFrame with the resultant operation's records.
        """
        extract_df = self._spark.createDataFrame(data=[], schema=schema)
        schema = extract_df.drop(omit_fields).schema.simpleString()
        return df.selectExpr(
            "*",
            f"from_json({self.auto_backtick(target_col)}, '{schema}') AS {self.auto_backtick(name)}",
        )

    def preserved_columns(
        self, df: DataFrame
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Performs unreferenced field preservation to new fields in the DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        # We do not want to preserve temporary fields.
        temp_columns = []
        if temp_fields := self._utils.get("temporaryFields", None):
            temp_columns = [f.get("name") for f in temp_fields]

        referenced_columns = self._referenced_columns()
        omitted_columns = self._omitted_columns()
        # omitted and referenced cols MAY be wrapped in backticks
        # so we need to check for their existence here on top of just plain col name
        preserved_columns = [
            col
            for col in df.columns
            if col not in referenced_columns
            and col not in omitted_columns
            and self.force_apply_backticks(col) not in referenced_columns
            and self.force_apply_backticks(col) not in omitted_columns
        ]
        duplicate_prefix = self._duplicate_prefix()
        column_names = self._column_names()
        duplicate_renames = [
            f"{self.auto_backtick(col)} AS {self.auto_backtick(duplicate_prefix + col)}"
            for col in preserved_columns
            if col in column_names
        ]
        preserved_columns = [
            col
            for col in preserved_columns
            if (col not in column_names and col not in temp_columns)
        ]
        column_names = [col for col in column_names if col not in preserved_columns]

        return (preserved_columns, duplicate_renames, column_names)

    def preserved_columns_embed_column(self, df) -> List[str]:
        """
        Performs unreferenced field preservation to new a single field in the DataFrame.
        (Serialized as JSON.)

        Returns:
            A DataFrame with the resultant operation's records.
        """
        referenced_columns = self._referenced_columns()
        omitted_columns = self._omitted_columns()
        preserved_columns = [
            col
            for col in df.columns
            if col not in referenced_columns and col not in omitted_columns
        ]
        return preserved_columns

    def insert_path(
        self, tree: Dict[str, Node], path: List[str], field: FieldSpec
    ) -> None:
        """
        Inserts a field specification into a tree of nodes.
        """
        if not path:
            return

        head = path[0]
        if len(path) == 1:
            tree[head] = Leaf(field)
        else:
            if head in tree and isinstance(tree[head], Branch):
                sub_tree = tree[head]._children
            else:
                sub_tree = {}
            self.insert_path(sub_tree, path[1:], field)
            tree[head] = Branch(sub_tree)

    def parse_to_tree(self, fields: List[FieldSpec]) -> Dict[str, Node]:
        """
        Parses a list of field specifications into a tree of nodes.
        """
        tree: Dict[str, Node] = {}
        for field in fields:
            name = field.get("name")
            if name is None:
                continue
            path = name.split(".")
            self.insert_path(tree, path, field)
        return tree

    def cast_to_expr(self, field: FieldSpec, name: str) -> str:
        """
        Casts a field specification into a SELECT expression.

        Returns:
            The SQL expression for the field.
        """
        if field.get("from", None):
            # check that the from column exists in the df?
            return f"{self.auto_backtick(field['from'])} AS {self.auto_backtick(name)}"
        elif field.get("literal", None):
            return f"'{field['literal']}' AS {self.auto_backtick(name)}"
        elif field.get("expr", None) is not None:
            return f"{field['expr']} AS {self.auto_backtick(name)}"
        else:
            return ""

    def is_backtick_escaped(self, name: str) -> bool:
        """
        check if a given (column) name is backtick escaped or not
        :param name: column name
        :return: bool
        """
        return name.startswith("`") and name.endswith("`")

    def auto_backtick(self, name: str) -> str:
        """
        auto-backtick given name in case it isn't already backtick escaped.
        if the name contains dots it will get split and each component backticked individually.
        Returns the name wrapped in backticks or the passed name if it already had backticks.
        :param name: column name
        :return: str
        """
        if self.is_backtick_escaped(name):
            return name
        parts = name.split(".")
        return ".".join(list(map(lambda s: f"`{s}`", parts)))

    def force_apply_backticks(self, name: str) -> str:
        """
        forces application of backticks to the given (column) name as a single unit
        if it already has backticks this is a noop
        :param name: column name
        :return: str
        """
        if self.is_backtick_escaped(name):
            return name
        return f"`{name}`"

    def process_node(self, name: str, node: Node) -> str:
        """
        Processes a single node in a tree of nodes.

        Returns:
            The STRUCT or SELECT SQL expression for the node.
        """
        if isinstance(node, Leaf):
            return self.cast_to_expr(node._field, name)
        elif isinstance(node, Branch):
            fields_list = []
            for child_name, child_node in node._children.items():
                child_expr = self.process_node(child_name, child_node)
                fields_list.append(f"{child_expr}")
            joined_fields = ",\n".join(fields_list)
            return f"struct(\n{joined_fields}\n) AS {self.auto_backtick(name)}"
        else:
            return ""

    def parse_to_string(self, nested_tree: Dict[str, Node]) -> str:
        """
        Processes the nested tree representation to a valid SELECT expression.

        Returns:
            The SQL expression.
        """
        lines = []
        for name, node in nested_tree.items():
            processed = self.process_node(name, node)
            wrapped = f"\n{processed}\n"
            lines.append(wrapped)
        return lines

    def render_fields(self, fields: List[FieldSpec]) -> str:
        """
        Renders a list of field specifications containing both simple and
        STRUCT references into valid, STRUCT cognicient, SELECT expressions.
        if a nested field is wrapped in backticks it will be treated as a simple field
        for example field of name `col.with.dots` will NOT be treated as nested field.

        Returns:
            The SQL expression.
        """
        simple_fields = [
            f
            for f in fields
            if "." not in f["name"] or self.is_backtick_escaped(f["name"])
        ]
        nested_fields = [
            f
            for f in fields
            if "." in f["name"] and not self.is_backtick_escaped(f["name"])
        ]

        result_parts = []
        for field in simple_fields:
            expr_str = self.cast_to_expr(field, field["name"])
            result_parts.append(f"{expr_str}")

        if nested_fields:
            tree = self.parse_to_tree(nested_fields)
            nested_str = self.parse_to_string(tree)
            result_parts.append(nested_str)

        return [p for p in result_parts if p is not None and len(p) > 0]

    def select_expr(self, df: DataFrame) -> str:
        """
        Renders all field specification operations that result in a SELECT expression
        after filtering, but before post-filtering and aliasing.

        Returns:
            The SQL expression.
        """
        select_fields = self.render_fields(self._fields)

        if preserve := self._utils.get("unreferencedColumns", None):
            should_preserve = preserve.get("preserve", None)
            if type(should_preserve) != bool:
                raise MissingUtilityConfigurationFieldError(
                    "unreferencedColumns", "preserve"
                )
            if should_preserve:
                if embed_col := preserve.get("embedColumn", None):
                    preserved_columns = self.preserved_columns_embed_column(df)
                    # preserved_columns is obtained from df.columns
                    # applying backticks to all of them is OK here
                    # since they will never use "obj.key" to reference nested fields of structs
                    # so we just go ahead and apply backticks to all across the board
                    select_fields += [
                        f"struct({', '.join(list(map(lambda x: self.force_apply_backticks(x), preserved_columns)))}) AS {self.auto_backtick(embed_col)}"
                    ]
                else:
                    (
                        preserved_columns,
                        duplicate_renames,
                        column_names,
                    ) = self.preserved_columns(df)
                    # see note above: same here - apply backticks to all columns across the board
                    select_fields += list(
                        map(lambda x: self.force_apply_backticks(x), preserved_columns)
                    )
                    select_fields += list(
                        map(lambda x: self.force_apply_backticks(x), duplicate_renames)
                    )

        return ["*"] + select_fields if self._stage == "temp_fields" else select_fields

    def run_filter(self, df: DataFrame) -> DataFrame:
        """
        Runs filter operations on the provided DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        if self._filter:
            df = df.filter(self._filter)
        return df

    def run_json_extract(self, df: DataFrame) -> DataFrame:
        """
        Runs JSON extract utility operations on the provided DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        if json_extracts := self._utils.get("jsonExtract", None):
            for json_extract in json_extracts:
                source = json_extract.get("source")
                if not source:
                    raise MissingUtilityConfigurationFieldError("jsonExtract", "source")
                omit_fields = json_extract.get("omitFields", [])
                duplicate_prefix = json_extract.get("duplicatePrefix", "d_")
                schema, columns = self.json_extract_boilerplate(
                    df, source, omit_fields, duplicate_prefix
                )
                if name := json_extract.get("embedColumn", None):
                    df = self.json_extract_embed_column(
                        df, schema, omit_fields, source, name
                    )
                else:
                    df = self.json_extract(df, schema, columns, source)
        return df

    def run_select_expr(self, df: DataFrame, select_fields: List[str]) -> DataFrame:
        """
        Runs select operations (preserver, from, literal, expr) on the provided DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        # Join columns, processed before this, need to be included in the
        # dataframe too. So we append their output names to the fields
        # selected.
        joins_cols = []
        for field in self._fields:
            if field.get("join", None):
                joins_cols += [field["name"]]

        return df.selectExpr(select_fields + joins_cols)

    def run_joins(self, df: DataFrame) -> DataFrame:
        """
        Runs joins operations on the provided DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        joins = []
        for field in self._fields:
            if field.get("join", None):
                joins += [field]

        for field in joins:
            join = field.get("join")
            lhs = join.get("lhs")
            if not lhs:
                raise MissingJoinFieldError("lhs")
            rhs = join.get("rhs")
            if not rhs:
                raise MissingJoinFieldError("rhs")
            select = join.get("select")
            if not select:
                raise MissingJoinFieldError("select")

            if table := join.get("withTable", None):
                df_joined = self._spark.table(table)
                df = (
                    df.alias("tmp")
                    .join(df_joined, on=[df[lhs] == df_joined[rhs]], how="left")
                    .selectExpr(
                        "tmp.*", f"{select} AS {self.auto_backtick(field.get('name'))}"
                    )
                )
            elif csv := join.get("withCSV", None):
                if path := csv.get("path", None):
                    df_joined = self._spark.read.csv(
                        path, header=True, inferSchema=True
                    )
                    df = (
                        df.alias("tmp")
                        .join(df_joined, on=[df[lhs] == df_joined[rhs]], how="left")
                        .selectExpr(
                            "tmp.*",
                            f"{select} AS {self.auto_backtick(field.get('name'))}",
                        )
                    )
            else:
                raise MissingJoinFieldError("withTable or withCSV (please supply 1)")
        return df

    def run_aliases(self, df: DataFrame) -> DataFrame:
        """
        Runs alias operations on the provided DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        for field in self._fields:
            if field.get("alias", None):
                df = df.selectExpr(
                    "*",
                    f"{self.auto_backtick(field.get('alias'))} AS {self.auto_backtick(field.get('name'))}",
                )
        return df

    def run_assertions(self, df: DataFrame) -> DataFrame:
        """
        Runs assert operations on the provided DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        for assertions in self._assertions:
            for assertion in assertions.get("assert"):
                failing_rows = df.filter(f"NOT ({assertion['expr']})")
                if not failing_rows.isEmpty():
                    raise AssertionFailedError(
                        assertion["expr"], assertion.get("message", ""), failing_rows
                    )
        return df

    def run_post_filter(self, df: DataFrame) -> DataFrame:
        """
        Runs postFilter operations on the provided DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        if self._postFilter:
            df = df.filter(self._postFilter)
        return df

    def run_temp_fields(self, df: DataFrame) -> DataFrame:
        """
        Runs temporary field expressions on the provided DataFrame.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        if temp_fields := self._utils.get("temporaryFields", None):
            df = Stage(self._spark, "temp_fields", {"fields": temp_fields}).run(df)
        return df

    def run(self, df: DataFrame) -> DataFrame:
        """
        Runs all provided preset operations in the provided stage's table.

        Returns:
            A DataFrame with the resultant operation's records.
        """
        df = self.run_filter(df)
        df = self.run_temp_fields(df)
        df = self.run_json_extract(df)
        df = self.run_joins(df)
        df = self.run_select_expr(df, self.select_expr(df))
        df = self.run_aliases(df)
        df = self.run_assertions(df)
        df = self.run_post_filter(df)
        return df
