from pydantic import BaseModel
from typing import Dict, List, Optional, Union

from dasl_api import (
    CoreV1Rule,
    CoreV1RuleSpec,
    CoreV1RuleSpecMetadata,
    CoreV1RuleSpecMetadataMitreInner,
    CoreV1RuleSpecMetadataResponse,
    CoreV1RuleSpecMetadataResponsePlaybooksInner,
    CoreV1RuleSpecInput,
    CoreV1RuleSpecInputBatch,
    CoreV1RuleSpecInputStream,
    CoreV1RuleSpecInputStreamCustom,
    CoreV1RuleSpecInputStreamTablesInner,
    CoreV1RuleSpecInputStreamTablesInnerWatermark,
    CoreV1RuleObservable,
    CoreV1RuleObservableRisk,
    CoreV1RuleSpecOutput,
    CoreV1RuleSpecCollate,
    CoreV1RuleSpecInputBatchCustom,
)

from .helpers import Helpers
from .types import Metadata, ResourceStatus, Schedule


class Rule(BaseModel):
    """
    Rules define how to generate notables from input data.

    Attributes:
        metadata (Optional[Metadata]):
            Standard object metadata.
        rule_metadata (Optional[Rule.RuleMetadata]):
            The rule configuration metadata.
        schedule (Schedule):
            The rule schedule.
        input (Rule.Input):
            The rule input configuration.
        observables (Optional[List[Rule.Observable]]):
            A list of observables.
        output (Rule.Output):
            The rule output configuration.
        collate (Optional[Rule.Collate]):
            The collate configuration.
        status (Optional[ResourceStatus]):
            The current status of the rule.
    """

    class RuleMetadata(BaseModel):
        """
        RuleMetadata object wrapping CoreV1RuleSpecMetadata.

        Attributes:
            version (Optional[Union[float, int]]):
                The current version of the rule.
            category (Optional[str]):
                The category of this detection. The available values are
                configured in workspace config.
            severity (Optional[str]):
                The threat level associated with the notable.
            fidelity (Optional[str]):
                Fidelity is used to capture the maturity of a rule. Newly
                created, untested rules should be marked as Investigative
                fidelity. Older, more well-tested rules should be marked as
                High fidelity. This helps an analyst determine how likely a
                notable is a false positive.
            mitre (Optional[List[Rule.RuleMetadata.Mitre]]):
                Mitre ATT&CK tactic information.
            objective (Optional[str]):
                A longer form description of what this rule is attempting to
                detect (objectMeta.comment is a summary).
            response (Optional[Rule.RuleMetadata.Response]):
                Response configuration for the rule.
        """

        class Mitre(BaseModel):
            """
            Mitre ATT&CK details associated with a Rule.

            Attributes:
                taxonomy (Optional[str]):
                    Mitre ATT&CK taxonomy.
                tactic (Optional[str]):
                    Mitre ATT&CK tactic.
                technique_id (Optional[str]):
                    The Mitre ATT&CK technique identifier.
                technique (Optional[str]):
                    The Mitre ATT&CK technique human-readable name.
                sub_technique_id (Optional[str]):
                    The Mitre ATT&CK sub-technique identifier.
                sub_technique (Optional[str]):
                    The Mitre ATT&CK sub-technique human-readable name.
            """

            taxonomy: Optional[str] = None
            tactic: Optional[str] = None
            technique_id: Optional[str] = None
            technique: Optional[str] = None
            sub_technique_id: Optional[str] = None
            sub_technique: Optional[str] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1RuleSpecMetadataMitreInner],
            ) -> "Rule.RuleMetadata.Mitre":
                if obj is None:
                    return None
                return Rule.RuleMetadata.Mitre(
                    taxonomy=obj.taxonomy,
                    tactic=obj.tactic,
                    technique_id=obj.technique_id,
                    technique=obj.technique,
                    sub_technique_id=obj.sub_technique_id,
                    sub_technique=obj.sub_technique,
                )

            def to_api_obj(self) -> CoreV1RuleSpecMetadataMitreInner:
                return CoreV1RuleSpecMetadataMitreInner(
                    taxonomy=self.taxonomy,
                    tactic=self.tactic,
                    technique_id=self.technique_id,
                    technique=self.technique,
                    sub_technique_id=self.sub_technique_id,
                    sub_technique=self.sub_technique,
                )

        class Response(BaseModel):
            """
            Details regarding how to respond to a notable generated
            by the Rule.

            Attributes:
                guidelines (Optional[str]):
                    Response guidelines.
                playbooks (Optional[List[Rule.RuleMetadata.Response.Playbook]]):
                    Suggested response playbooks.
            """

            class Playbook(BaseModel):
                """
                Databricks notebook and template values to generate a playbook
                for the analyst from the notable.

                Attributes:
                    notebook (Optional[str]):
                        Notebook to run.
                    options (Optional[Dict[str, str]]):
                        These are templated, if they contain ${} this will be
                        filled in using the notable.
                """

                notebook: Optional[str] = None
                options: Optional[Dict[str, str]] = None

                @staticmethod
                def from_api_obj(
                    obj: Optional[CoreV1RuleSpecMetadataResponsePlaybooksInner],
                ) -> "Rule.RuleMetadata.Response.Playbook":
                    if obj is None:
                        return None
                    return Rule.RuleMetadata.Response.Playbook(
                        notebook=obj.notebook,
                        options=obj.options,
                    )

                def to_api_obj(self) -> CoreV1RuleSpecMetadataResponsePlaybooksInner:
                    return CoreV1RuleSpecMetadataResponsePlaybooksInner(
                        notebook=self.notebook,
                        options=self.options,
                    )

            guidelines: Optional[str] = None
            playbooks: Optional[List["Rule.RuleMetadata.Response.Playbook"]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1RuleSpecMetadataResponse],
            ) -> "Rule.RuleMetadata.Response":
                if obj is None:
                    return None
                playbooks = None
                if obj.playbooks is not None:
                    playbooks = [
                        Rule.RuleMetadata.Response.Playbook.from_api_obj(item)
                        for item in obj.playbooks
                    ]
                return Rule.RuleMetadata.Response(
                    guidelines=obj.guidelines,
                    playbooks=playbooks,
                )

            def to_api_obj(self) -> CoreV1RuleSpecMetadataResponse:
                playbooks = None
                if self.playbooks is not None:
                    playbooks = [item.to_api_obj() for item in self.playbooks]
                return CoreV1RuleSpecMetadataResponse(
                    guidelines=self.guidelines,
                    playbooks=playbooks,
                )

        version: Optional[Union[float, int]] = None
        category: Optional[str] = None
        severity: Optional[str] = None
        fidelity: Optional[str] = None
        mitre: Optional[List["Rule.RuleMetadata.Mitre"]] = None
        objective: Optional[str] = None
        response: Optional["Rule.RuleMetadata.Response"] = None

        @staticmethod
        def from_api_obj(obj: Optional[CoreV1RuleSpecMetadata]) -> "Rule.RuleMetadata":
            if obj is None:
                return None
            mitre = None
            if obj.mitre is not None:
                mitre = [
                    Rule.RuleMetadata.Mitre.from_api_obj(item) for item in obj.mitre
                ]
            return Rule.RuleMetadata(
                version=obj.version,
                category=obj.category,
                severity=obj.severity,
                fidelity=obj.fidelity,
                mitre=mitre,
                objective=obj.objective,
                response=Rule.RuleMetadata.Response.from_api_obj(obj.response),
            )

        def to_api_obj(self) -> CoreV1RuleSpecMetadata:
            mitre = None
            if self.mitre is not None:
                mitre = [item.to_api_obj() for item in self.mitre]
            return CoreV1RuleSpecMetadata(
                version=self.version,
                category=self.category,
                severity=self.severity,
                fidelity=self.fidelity,
                mitre=mitre,
                objective=self.objective,
                response=Helpers.maybe(lambda o: o.to_api_obj(), self.response),
            )

    class Input(BaseModel):
        """
        Specification of input data for the Rule.

        Attributes:
            stream (Optional[Rule.Input.Stream]):
                Input if the Rule should operate on streaming input data.
            batch (Optional[Rule.Input.Batch]):
                Input if the rule should operate on batched input data.
        """

        class CustomStream(BaseModel):
            """
            Specification of a stream custom notebook for generating input to
            the Rule.

            Attributes:
                notebook (Optional[str]):
                options (Optional[Dict[str, str]]):
            """

            notebook: Optional[str] = None
            options: Optional[Dict[str, str]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1RuleSpecInputStreamCustom],
            ) -> "Rule.Input.CustomStream":
                if obj is None:
                    return None
                return Rule.Input.CustomStream(
                    notebook=obj.notebook,
                    options=obj.options,
                )

            def to_api_obj(self) -> CoreV1RuleSpecInputStreamCustom:
                return CoreV1RuleSpecInputStreamCustom(
                    notebook=self.notebook,
                    options=self.options,
                )

        class CustomBatch(BaseModel):
            """
            Specification of a batch custom notebook for generating input to
            the Rule.

            Attributes:
                notebook (Optional[str]):
                options (Optional[Dict[str, str]]):
            """

            notebook: Optional[str] = None
            options: Optional[Dict[str, str]] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1RuleSpecInputBatchCustom],
            ) -> "Rule.Input.CustomBatch":
                if obj is None:
                    return None
                return Rule.Input.CustomBatch(
                    notebook=obj.notebook,
                    options=obj.options,
                )

            def to_api_obj(self) -> CoreV1RuleSpecInputBatchCustom:
                return CoreV1RuleSpecInputBatchCustom(
                    notebook=self.notebook,
                    options=self.options,
                )

        class Stream(BaseModel):
            """
            Specification for streaming input from a table or tables,
            from a custom notebook, or directly from a SQL statement.

            Attributes:
                tables (Optional[List[Rule.Input.Stream.Table]]):
                filter (Optional[str]):
                sql (Optional[str]):
                custom (Optional[Rule.Input.CustomStream]):
            """

            class Table(BaseModel):
                """
                Specification of a table for streaming input.

                Attributes:
                    name (Optional[str]):
                        Name of the table.
                    watermark (Optional[Rule.Input.Stream.Table.Watermark]):
                        Watermark configuration.
                    alias (Optional[str]):
                        Alias name for the table.
                    join_type (Optional[str]):
                        For tables other than the first, how to join to the
                        preceding table.
                    join_expr (Optional[str]):
                        For tables other than the first, the join condition
                        expression to join with the preceding table.
                    streaming (Optional[bool]):
                        For tables other than the first, is this a streaming
                        join or static. Default is false, except on the first
                        table.
                """

                class Watermark(BaseModel):
                    """
                    Watermark for a streaming input table.

                    Attributes:
                        event_time_column (str):
                            Which column is the event time for the delay
                            threshold.
                        delay_threshold (str):
                            A time duration string for the watermark delay.
                        drop_duplicates (Optional[List[str]]):
                            Pass into pyspark dropDuplicates (effectively
                            columns for group by).
                    """

                    event_time_column: str
                    delay_threshold: str
                    drop_duplicates: Optional[List[str]] = None

                    @staticmethod
                    def from_api_obj(
                        obj: Optional[CoreV1RuleSpecInputStreamTablesInnerWatermark],
                    ) -> "Rule.Input.Stream.Table.Watermark":
                        if obj is None:
                            return None
                        return Rule.Input.Stream.Table.Watermark(
                            event_time_column=obj.event_time_column,
                            delay_threshold=obj.delay_threshold,
                            drop_duplicates=obj.drop_duplicates,
                        )

                    def to_api_obj(
                        self,
                    ) -> CoreV1RuleSpecInputStreamTablesInnerWatermark:
                        return CoreV1RuleSpecInputStreamTablesInnerWatermark(
                            event_time_column=self.event_time_column,
                            delay_threshold=self.delay_threshold,
                            drop_duplicates=self.drop_duplicates,
                        )

                name: Optional[str] = None
                watermark: Optional["Rule.Input.Stream.Table.Watermark"] = None
                alias: Optional[str] = None
                join_type: Optional[str] = None
                join_expr: Optional[str] = None
                streaming: Optional[bool] = None

                @staticmethod
                def from_api_obj(
                    obj: Optional[CoreV1RuleSpecInputStreamTablesInner],
                ) -> "Rule.Input.Stream.Table":
                    if obj is None:
                        return None
                    return Rule.Input.Stream.Table(
                        name=obj.name,
                        watermark=Rule.Input.Stream.Table.Watermark.from_api_obj(
                            obj.watermark
                        ),
                        alias=obj.alias,
                        join_type=obj.join_type,
                        join_expr=obj.join_expr,
                        streaming=obj.streaming,
                    )

                def to_api_obj(self) -> CoreV1RuleSpecInputStreamTablesInner:
                    return CoreV1RuleSpecInputStreamTablesInner(
                        name=self.name,
                        watermark=Helpers.maybe(
                            lambda o: o.to_api_obj(), self.watermark
                        ),
                        alias=self.alias,
                        join_type=self.join_type,
                        join_expr=self.join_expr,
                        streaming=self.streaming,
                    )

            tables: Optional[List["Rule.Input.Stream.Table"]] = None
            filter: Optional[str] = None
            sql: Optional[str] = None
            custom: Optional["Rule.Input.CustomStream"] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1RuleSpecInputStream],
            ) -> "Rule.Input.Stream":
                if obj is None:
                    return None
                tables = None
                if obj.tables is not None:
                    tables = [
                        Rule.Input.Stream.Table.from_api_obj(item)
                        for item in obj.tables
                    ]
                return Rule.Input.Stream(
                    tables=tables,
                    filter=obj.filter,
                    sql=obj.sql,
                    custom=Rule.Input.CustomStream.from_api_obj(obj.custom),
                )

            def to_api_obj(self) -> CoreV1RuleSpecInputStream:
                tables = None
                if self.tables is not None:
                    tables = [item.to_api_obj() for item in self.tables]
                return CoreV1RuleSpecInputStream(
                    tables=tables,
                    filter=self.filter,
                    sql=self.sql,
                    custom=Helpers.maybe(lambda o: o.to_api_obj(), self.custom),
                )

        class Batch(BaseModel):
            """
            Specification for batch input to a Rule, either from a
            SQL statement or a custom notebook.

            Attributes:
                sql (Optional[str]):
                custom (Optional[Rule.Input.CustomBatch]):
            """

            sql: Optional[str] = None
            custom: Optional["Rule.Input.CustomBatch"] = None

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1RuleSpecInputBatch],
            ) -> "Rule.Input.Batch":
                if obj is None:
                    return None
                return Rule.Input.Batch(
                    sql=obj.sql,
                    custom=Rule.Input.CustomBatch.from_api_obj(obj.custom),
                )

            def to_api_obj(self) -> CoreV1RuleSpecInputBatch:
                return CoreV1RuleSpecInputBatch(
                    sql=self.sql,
                    custom=Helpers.maybe(lambda o: o.to_api_obj(), self.custom),
                )

        stream: Optional["Rule.Input.Stream"] = None
        batch: Optional["Rule.Input.Batch"] = None

        @staticmethod
        def from_api_obj(obj: Optional[CoreV1RuleSpecInput]) -> "Rule.Input":
            return Rule.Input(
                stream=Rule.Input.Stream.from_api_obj(obj.stream),
                batch=Rule.Input.Batch.from_api_obj(obj.batch),
            )

        def to_api_obj(self) -> CoreV1RuleSpecInput:
            to_api_obj = lambda o: o.to_api_obj()
            return CoreV1RuleSpecInput(
                stream=Helpers.maybe(to_api_obj, self.stream),
                batch=Helpers.maybe(to_api_obj, self.batch),
            )

    class Observable(BaseModel):
        """
        Observable associated with a Rule.

        Attributes:
            kind (str):
            value (str):
            relationship (str):
            risk (Rule.Observable.Risk):
        """

        class Risk(BaseModel):
            """
            Risk level associated with an Observable.

            Attributes:
                impact (str):
                    A SQL expression indicating the impact (should evaluate to
                    a number between 0-100).
                confidence (str):
                    A SQL expression indicating the confidence (should
                    evaluate to a number between 0-100).
            """

            impact: str
            confidence: str

            @staticmethod
            def from_api_obj(
                obj: Optional[CoreV1RuleObservableRisk],
            ) -> "Rule.Observable.Risk":
                if obj is None:
                    return None
                return Rule.Observable.Risk(
                    impact=obj.impact,
                    confidence=obj.confidence,
                )

            def to_api_obj(self) -> CoreV1RuleObservableRisk:
                return CoreV1RuleObservableRisk(
                    impact=self.impact,
                    confidence=self.confidence,
                )

        kind: str
        value: str
        relationship: str
        risk: "Rule.Observable.Risk"

        @staticmethod
        def from_api_obj(obj: Optional[CoreV1RuleObservable]) -> "Rule.Observable":
            if obj is None:
                return None
            return Rule.Observable(
                kind=obj.kind,
                value=obj.value,
                relationship=obj.relationship,
                risk=Rule.Observable.Risk.from_api_obj(obj.risk),
            )

        def to_api_obj(self) -> CoreV1RuleObservable:
            return CoreV1RuleObservable(
                kind=self.kind,
                value=self.value,
                relationship=self.relationship,
                risk=self.risk.to_api_obj(),
            )

    class Output(BaseModel):
        """
        Output from a Rule after matching.

        Attributes:
            summary (Optional[str]):
            context (Optional[Dict[str, str]]):
        """

        summary: Optional[str] = None
        context: Optional[Dict[str, str]] = None

        @staticmethod
        def from_api_obj(obj: Optional[CoreV1RuleSpecOutput]) -> "Rule.Output":
            if obj is None:
                return None
            return Rule.Output(
                summary=obj.summary,
                context=obj.context,
            )

        def to_api_obj(self) -> CoreV1RuleSpecOutput:
            return CoreV1RuleSpecOutput(
                summary=self.summary,
                context=self.context,
            )

    class Collate(BaseModel):
        """
        Configuration for collating multiple notables generated from a Rule
        within a given timeframe.

        Attributes:
            collate_on (Optional[List[str]]):
                SQL column(s) to collate notables on. This must be either
                'summary', 'context', or a JSON key within 'context'. Only
                one level of nesting is currently supported.
            within (Optional[str]):
                A time duration string for the window to collate within.
            action (Optional[str]):
                append | updateStats | inhibit.
        """

        collate_on: Optional[List[str]] = None
        within: Optional[str] = None
        action: Optional[str] = None

        @staticmethod
        def from_api_obj(obj: Optional[CoreV1RuleSpecCollate]) -> "Rule.Collate":
            if obj is None:
                return None
            return Rule.Collate(
                collate_on=obj.collate_on,
                within=obj.within,
                action=obj.action,
            )

        def to_api_obj(self) -> CoreV1RuleSpecCollate:
            return CoreV1RuleSpecCollate(
                collate_on=self.collate_on,
                within=self.within,
                action=self.action,
            )

    metadata: Optional[Metadata] = None
    rule_metadata: Optional["Rule.RuleMetadata"] = None
    schedule: Schedule
    input: "Rule.Input"
    observables: Optional[List["Rule.Observable"]] = None
    output: "Rule.Output"
    collate: Optional["Rule.Collate"] = None
    status: Optional[ResourceStatus] = None

    @staticmethod
    def from_api_obj(obj: CoreV1Rule) -> "Rule":
        observables = None
        if obj.spec.observables is not None:
            observables = [
                Rule.Observable.from_api_obj(item) for item in obj.spec.observables
            ]
        return Rule(
            metadata=Metadata.from_api_obj(obj.metadata),
            rule_metadata=Rule.RuleMetadata.from_api_obj(obj.spec.metadata),
            schedule=Schedule.from_api_obj(obj.spec.schedule),
            input=Rule.Input.from_api_obj(obj.spec.input),
            observables=observables,
            output=Rule.Output.from_api_obj(obj.spec.output),
            collate=Rule.Collate.from_api_obj(obj.spec.collate),
            status=ResourceStatus.from_api_obj(obj.status),
        )

    def to_api_obj(self) -> CoreV1Rule:
        observables = None
        if self.observables is not None:
            observables = [item.to_api_obj() for item in self.observables]
        to_api_obj = lambda o: o.to_api_obj()
        return CoreV1Rule(
            api_version="v1",
            kind="Rule",
            metadata=Helpers.maybe(to_api_obj, self.metadata),
            spec=CoreV1RuleSpec(
                metadata=Helpers.maybe(to_api_obj, self.rule_metadata),
                schedule=self.schedule.to_api_obj(),
                input=self.input.to_api_obj(),
                observables=observables,
                output=self.output.to_api_obj(),
                collate=Helpers.maybe(to_api_obj, self.collate),
            ),
            status=Helpers.maybe(to_api_obj, self.status),
        )
