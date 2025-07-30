from dasl_client import *

from .constants import *


def test_workspace_config_marshal_unmarshal():
    workspace_config = WorkspaceConfig(
        metadata=Metadata(
            name="config",
            workspace=workspace,
            comment="a random comment",
            annotations={"key1": "value1", "key2": "value2"},
            created_timestamp=datetime(2023, 1, 1, 12, 30),
            created_by="creator_user",
            modified_timestamp=datetime(2023, 1, 2, 13, 45),
            last_successful_run_timestamp=datetime(2023, 1, 3, 14, 0),
            modified_by="modifier_user",
            version=1,
            deleted=False,
            resource_status="none",
            ui_status="ok",
            client_of_origin=get_client_identifier(),
        ),
        system_tables_config=SystemTablesConfig(
            catalog_name="catalog_random", var_schema="schema_random"
        ),
        default_sql_warehouse="warehouse_random",
        detection_rule_metadata=DetectionRuleMetadata(
            detection_categories=["category1", "category2"]
        ),
        notable_export=ExportConfig(
            destination="webhook",
            export_open_only=True,
            webhook_config=ExportConfig.WebhookConfig(
                destination=ExportConfig.WebhookDestination(
                    value="wh_value1", scope="wh_scope1", key="wh_key1"
                )
            ),
            slack_config=ExportConfig.SlackConfig(
                token=ExportConfig.WebhookDestination(
                    value="slack_token1", scope="slack_scope1", key="slack_key1"
                ),
                channel="#channel1",
                message="slack message 1",
            ),
        ),
        operational_alert_export=ExportConfig(
            destination="slack",
            export_open_only=False,
            webhook_config=ExportConfig.WebhookConfig(
                destination=ExportConfig.WebhookDestination(
                    value="wh_value2", scope="wh_scope2", key="wh_key2"
                )
            ),
            slack_config=ExportConfig.SlackConfig(
                token=ExportConfig.WebhookDestination(
                    value="slack_token2", scope="slack_scope2", key="slack_key2"
                ),
                channel="#channel2",
                message="slack message 2",
            ),
        ),
        observables=WorkspaceConfigObservables(
            kinds=[
                WorkspaceConfigObservables.ObservablesKinds(
                    name="kind1", sql_type="type1"
                ),
                WorkspaceConfigObservables.ObservablesKinds(
                    name="kind2", sql_type="type2"
                ),
            ],
            relationships=["rel1", "rel2"],
        ),
        dasl_storage_path="/random/storage/path",
        default_config=DefaultConfig(
            datasources=DefaultConfig.Config(
                notebook_location="notebook_ds",
                bronze_schema="bronze_ds",
                silver_schema="silver_ds",
                gold_schema="gold_ds",
                catalog_name="catalog_ds",
                default_max_resources_per_job=5,
                checkpoint_location="checkpoint_ds",
                compute_group_overrides={
                    "override1": DefaultConfig.Config.ComputeGroupOverrides(
                        max_resources_per_job=2
                    ),
                    "override2": DefaultConfig.Config.ComputeGroupOverrides(
                        max_resources_per_job=3
                    ),
                },
            ),
            transforms=DefaultConfig.Config(
                notebook_location="notebook_trans",
                bronze_schema="bronze_trans",
                silver_schema="silver_trans",
                gold_schema="gold_trans",
                catalog_name="catalog_trans",
                default_max_resources_per_job=6,
                checkpoint_location="checkpoint_trans",
                compute_group_overrides={
                    "override3": DefaultConfig.Config.ComputeGroupOverrides(
                        max_resources_per_job=4
                    ),
                    "override4": DefaultConfig.Config.ComputeGroupOverrides(
                        max_resources_per_job=5
                    ),
                },
            ),
            rules=DefaultConfig.Config(
                notebook_location="notebook_rules",
                bronze_schema="bronze_rules",
                silver_schema="silver_rules",
                gold_schema="gold_rules",
                catalog_name="catalog_rules",
                default_max_resources_per_job=7,
                checkpoint_location="checkpoint_rules",
                compute_group_overrides={
                    "override5": DefaultConfig.Config.ComputeGroupOverrides(
                        max_resources_per_job=6
                    ),
                    "override6": DefaultConfig.Config.ComputeGroupOverrides(
                        max_resources_per_job=7
                    ),
                },
            ),
            var_global=DefaultConfig.Config(
                notebook_location="notebook_var",
                bronze_schema="bronze_var",
                silver_schema="silver_var",
                gold_schema="gold_var",
                catalog_name="catalog_var",
                default_max_resources_per_job=8,
                checkpoint_location="checkpoint_var",
                compute_group_overrides={
                    "override7": DefaultConfig.Config.ComputeGroupOverrides(
                        max_resources_per_job=8
                    ),
                    "override8": DefaultConfig.Config.ComputeGroupOverrides(
                        max_resources_per_job=9
                    ),
                },
            ),
        ),
        managed_retention=[
            ManagedRetention(
                catalog="catalog_ret1",
                var_schema="schema_ret1",
                column="col_ret1",
                duration="1d",
                overrides=[
                    ManagedRetention.Overrides(
                        table="table1", column="colA", duration="1h"
                    ),
                    ManagedRetention.Overrides(
                        table="table2", column="colB", duration="2h"
                    ),
                ],
            ),
            ManagedRetention(
                catalog="catalog_ret2",
                var_schema="schema_ret2",
                column="col_ret2",
                duration="2d",
                overrides=[
                    ManagedRetention.Overrides(
                        table="table3", column="colC", duration="3h"
                    ),
                    ManagedRetention.Overrides(
                        table="table4", column="colD", duration="4h"
                    ),
                ],
            ),
        ],
        status=ResourceStatus(
            job_id=123,
            job_name="job_random",
            enabled=True,
            notebook_path="/path/to/notebook",
            created_at=datetime(2023, 1, 4, 15, 0),
            job_status="scheduled",
            events=[
                ResourceStatus.StatusEvent(
                    action="create",
                    message="job started",
                    recorded_at=datetime(2023, 1, 4, 15, 0),
                ),
                ResourceStatus.StatusEvent(
                    action="update",
                    message="job finished",
                    recorded_at=datetime(2023, 1, 4, 16, 0),
                ),
            ],
        ),
    )

    assert workspace_config == WorkspaceConfig.from_api_obj(
        workspace_config.to_api_obj()
    )


def test_data_source_marshal_unmarshal():
    data_source = DataSource(
        metadata=Metadata(
            name="data_source_name",
            workspace="workspace1",
            comment="A sample data source",
            annotations={"env": "prod", "version": "v1"},
            created_timestamp=datetime(2023, 4, 1, 10, 0),
            created_by="creator_ds",
            modified_timestamp=datetime(2023, 4, 2, 11, 30),
            last_successful_run_timestamp=datetime(2023, 4, 3, 12, 45),
            modified_by="modifier_ds",
            version=2,
            deleted=False,
            resource_status="deletionPending",
            ui_status="ok",
            client_of_origin=get_client_identifier(),
        ),
        source="s3://data-bucket/source",
        source_type="custom",
        schedule=Schedule(
            at_least_every="1h",
            exactly="1h",
            continuous=True,
            compute_group="compute_group1",
            enabled=True,
        ),
        custom=DataSource.CustomNotebook(
            notebook="print('Hello from custom notebook')"
        ),
        use_preset="preset_alpha",
        autoloader=DataSource.Autoloader(
            format="json",
            location="s3://data-bucket/autoloader",
            schema_file="schema_autoloader.json",
            cloud_files=DataSource.Autoloader.CloudFiles(
                schema_hints_file="hints.txt", schema_hints="hint1, hint2"
            ),
        ),
        bronze=BronzeSpec(
            clustering=BronzeSpec.Clustering(
                column_names=["cluster_col1", "cluster_col2"], time_column="timestamp"
            ),
            bronze_table="bronze_table_1",
            skip_bronze_loading=False,
        ),
        silver=SilverSpec(
            bronze_tables=[
                SilverSpec.BronzeTable(
                    name="silver_bronze_table_1",
                    streaming=True,
                    watermark=SilverSpec.BronzeTable.Watermark(
                        event_time_column="event_time",
                        delay_threshold="10m",
                        drop_duplicates=["dup1", "dup2"],
                    ),
                    alias="silver_alias",
                    join_type="inner",
                    join_expr="a.id = b.id",
                ),
            ],
            pre_transform=SilverSpec.PreTransform(
                use_preset="silver_pre",
                skip_pre_transform=False,
                custom=SilverSpec.PreTransform.Custom(
                    function="pre_transform_func",
                    options={"option1": "value1", "option2": "value2"},
                ),
                filter="col > 0",
                post_filter="col < 100",
                preset_overrides=SilverSpec.PreTransform.PresetOverrides(
                    omit_fields=["omit_field1", "omit_field2"]
                ),
                add_fields=[
                    FieldSpec(
                        name="pre_field1",
                        comment="Pre transform field 1",
                        var_assert=[
                            FieldSpec.Assert(expr="x > 0", message="x must be positive")
                        ],
                        var_from="source_x",
                        alias="alias_x",
                        expr="x + 1",
                        literal="10",
                        join=FieldSpec.Join(
                            with_table="join_table_1",
                            with_csv=FieldSpec.Join.WithCSV(path="/path/to/join1.csv"),
                            lhs="x",
                            rhs="y",
                            select="x, y",
                        ),
                    ),
                    FieldSpec(
                        name="pre_field2",
                        comment="Pre transform field 2",
                        var_assert=[
                            FieldSpec.Assert(expr="y != 0", message="y must be nonzero")
                        ],
                        var_from="source_y",
                        alias="alias_y",
                        expr="y * 2",
                        literal="20",
                        join=FieldSpec.Join(
                            with_table="join_table_2",
                            with_csv=FieldSpec.Join.WithCSV(path="/path/to/join2.csv"),
                            lhs="y",
                            rhs="z",
                            select="y, z",
                        ),
                    ),
                ],
            ),
            transform=SilverSpec.Transform(
                skip_silver_transform=False,
                preset_overrides=SilverSpec.Transform.PresetOverrides(
                    modify_tables=[
                        SilverSpec.Transform.PresetOverrides.ModifyTables(
                            name="modify_table1",
                            custom=SilverSpec.Transform.PresetOverrides.Custom(
                                function="modify_func1",
                                options={"mod_opt1": "val1", "mod_opt2": "val2"},
                            ),
                            omit_fields=["mod_omit1", "mod_omit2"],
                            override_liquid_columns=["liq1", "liq2"],
                            add_fields=[
                                FieldSpec(
                                    name="mod_field1",
                                    comment="Modify field 1",
                                    var_assert=[
                                        FieldSpec.Assert(
                                            expr="a < b",
                                            message="a should be less than b",
                                        )
                                    ],
                                    var_from="mod_source1",
                                    alias="mod_alias1",
                                    expr="a - b",
                                    literal="5",
                                    join=FieldSpec.Join(
                                        with_table="mod_join_table",
                                        with_csv=FieldSpec.Join.WithCSV(
                                            path="/path/to/mod_join.csv"
                                        ),
                                        lhs="a",
                                        rhs="b",
                                        select="a, b",
                                    ),
                                )
                            ],
                            filter="mod_filter > 0",
                            post_filter="mod_post_filter < 100",
                            utils=FieldUtils(
                                unreferenced_columns=FieldUtils.UnreferencedColumns(
                                    preserve=False,
                                    embed_column="mod_embed",
                                    omit_columns=["mod_omit_col1", "mod_omit_col2"],
                                    duplicate_prefix="mod_dup_",
                                ),
                                json_extract=[
                                    FieldUtils.JsonExtract(
                                        source="mod_json_source",
                                        omit_fields=[
                                            "mod_json_omit1",
                                            "mod_json_omit2",
                                        ],
                                        duplicate_prefix="mod_json_dup_",
                                        embed_column="mod_json_embed",
                                    )
                                ],
                            ),
                        )
                    ],
                    omit_tables=["omit_table1", "omit_table2"],
                    add_tables=[
                        SilverSpec.Transform.PresetOverrides.AddTables(
                            custom=SilverSpec.Transform.PresetOverrides.Custom(
                                function="add_func1",
                                options={"add_opt1": "val1", "add_opt2": "val2"},
                            ),
                            name="add_table1",
                            filter="add_filter_condition",
                            post_filter="add_post_filter_condition",
                            override_liquid_columns=["add_liq1", "add_liq2"],
                            fields=[
                                FieldSpec(
                                    name="add_field1",
                                    comment="Add table field 1",
                                    var_assert=[
                                        FieldSpec.Assert(
                                            expr="c == 1", message="c must equal 1"
                                        )
                                    ],
                                    var_from="add_source1",
                                    alias="add_alias1",
                                    expr="c + 10",
                                    literal="15",
                                    join=FieldSpec.Join(
                                        with_table="add_join_table",
                                        with_csv=FieldSpec.Join.WithCSV(
                                            path="/path/to/add_join.csv"
                                        ),
                                        lhs="c",
                                        rhs="d",
                                        select="c, d",
                                    ),
                                )
                            ],
                            utils=FieldUtils(
                                unreferenced_columns=FieldUtils.UnreferencedColumns(
                                    preserve=True,
                                    embed_column="add_embed",
                                    omit_columns=["add_omit1", "add_omit2"],
                                    duplicate_prefix="add_dup_",
                                ),
                                json_extract=[
                                    FieldUtils.JsonExtract(
                                        source="add_json_source",
                                        omit_fields=[
                                            "add_json_omit1",
                                            "add_json_omit2",
                                        ],
                                        duplicate_prefix="add_json_dup_",
                                        embed_column="add_json_embed",
                                    )
                                ],
                            ),
                        )
                    ],
                ),
            ),
        ),
        gold=GoldSpec(
            omit_tables=["gold_omit1", "gold_omit2"],
            modify_tables=[
                GoldSpec.ModifyTables(
                    name="gold_modify_table1",
                    source_table="gold_source_table1",
                    custom=GoldSpec.ModifyTables.Custom(
                        function="gold_modify_func",
                        options={"gold_opt1": "val1", "gold_opt2": "val2"},
                    ),
                    omit_fields=["gold_field_omit1", "gold_field_omit2"],
                    add_fields=[
                        FieldSpec(
                            name="gold_field1",
                            comment="Gold modify field 1",
                            var_assert=[
                                FieldSpec.Assert(
                                    expr="z != 0", message="z must not be zero"
                                )
                            ],
                            var_from="gold_source",
                            alias="gold_alias",
                            expr="z / 2",
                            literal="3.14",
                            join=FieldSpec.Join(
                                with_table="gold_join_table",
                                with_csv=FieldSpec.Join.WithCSV(
                                    path="/path/to/gold_join.csv"
                                ),
                                lhs="z",
                                rhs="w",
                                select="z, w",
                            ),
                        )
                    ],
                    filter="gold_filter_condition",
                    post_filter="gold_post_filter_condition",
                )
            ],
            add_tables=[
                GoldSpec.AddTables(
                    name="gold_add_table1",
                    source_table="gold_add_source_table1",
                    custom=GoldSpec.AddTables.Custom(
                        function="gold_add_func",
                        options={"gold_add_opt1": "val1", "gold_add_opt2": "val2"},
                    ),
                    filter="gold_add_filter_condition",
                    post_filter="gold_add_post_filter_condition",
                    fields=[
                        FieldSpec(
                            name="gold_add_field1",
                            comment="Gold add field 1",
                            var_assert=[
                                FieldSpec.Assert(
                                    expr="a > 0", message="a must be positive"
                                )
                            ],
                            var_from="gold_add_source",
                            alias="gold_add_alias",
                            expr="a + 10",
                            literal="20",
                            join=FieldSpec.Join(
                                with_table="gold_add_join_table",
                                with_csv=FieldSpec.Join.WithCSV(
                                    path="/path/to/gold_add_join.csv"
                                ),
                                lhs="a",
                                rhs="b",
                                select="a, b",
                            ),
                        )
                    ],
                ),
            ],
        ),
        status=ResourceStatus(
            job_id=789,
            job_name="data_source_job",
            enabled=True,
            notebook_path="/path/to/datasource/notebook",
            created_at=datetime(2023, 5, 1, 8, 0),
            job_status="unscheduled",
            events=[
                ResourceStatus.StatusEvent(
                    action="create",
                    message="Data source job started",
                    recorded_at=datetime(2023, 5, 1, 8, 0),
                ),
                ResourceStatus.StatusEvent(
                    action="update",
                    message="Data source job finished",
                    recorded_at=datetime(2023, 5, 1, 8, 30),
                ),
            ],
        ),
    )

    assert data_source == DataSource.from_api_obj(data_source.to_api_obj())


def test_rule_marshal_unmarshal():
    rule = Rule(
        metadata=Metadata(
            name="rule_meta_name",
            workspace="example_workspace",
            comment="This is a sample rule metadata comment.",
            annotations={"env": "prod", "source": "system"},
            created_timestamp=datetime(2023, 1, 1, 9, 0),
            created_by="rule_creator",
            modified_timestamp=datetime(2023, 1, 2, 10, 0),
            last_successful_run_timestamp=datetime(2023, 1, 3, 11, 0),
            modified_by="rule_modifier",
            version=1,
            deleted=False,
            resource_status="none",
            ui_status="ok",
            client_of_origin=get_client_identifier(),
        ),
        rule_metadata=Rule.RuleMetadata(
            version=1.0,
            category="Security",
            severity="High",
            fidelity="Investigative",
            mitre=[
                Rule.RuleMetadata.Mitre(
                    taxonomy="MITRE ATT&CK",
                    tactic="Initial Access",
                    technique_id="T1190",
                    technique="Exploit Public-Facing Application",
                    sub_technique_id="T1190.001",
                    sub_technique="Example Sub-technique",
                )
            ],
            objective="Detect unauthorized access attempts",
            response=Rule.RuleMetadata.Response(
                guidelines="Follow the incident response plan immediately.",
                playbooks=[
                    Rule.RuleMetadata.Response.Playbook(
                        notebook="incident_response.ipynb",
                        options={"notify": "email", "severity": "high"},
                    )
                ],
            ),
        ),
        schedule=Schedule(
            at_least_every="15m",
            exactly="15m",
            continuous=True,
            compute_group="rule_compute_group",
            enabled=True,
        ),
        input=Rule.Input(
            stream=Rule.Input.Stream(
                tables=[
                    Rule.Input.Stream.Table(
                        name="access_logs",
                        watermark=Rule.Input.Stream.Table.Watermark(
                            event_time_column="timestamp",
                            delay_threshold="5m",
                            drop_duplicates=["ip", "user_id"],
                        ),
                        alias="logs",
                        join_type="inner",
                        join_expr="access_logs.user_id = user_info.id",
                    ),
                    Rule.Input.Stream.Table(
                        name="user_info",
                        watermark=Rule.Input.Stream.Table.Watermark(
                            event_time_column="event_time",
                            delay_threshold="10m",
                            drop_duplicates=["id"],
                        ),
                        alias="users",
                        join_type="left",
                        join_expr="user_info.id = access_logs.user_id",
                    ),
                ],
                filter="status = 'active'",
                sql="SELECT * FROM streaming_source",
                custom=Rule.Input.CustomStream(
                    notebook="stream_custom.ipynb",
                    options={"filter": "recent", "limit": "1000"},
                ),
            ),
            batch=Rule.Input.Batch(
                sql="SELECT * FROM historical_source",
                custom=Rule.Input.CustomBatch(
                    notebook="batch_custom.ipynb",
                    options={"start_date": "2022-01-01", "end_date": "2022-12-31"},
                ),
            ),
        ),
        observables=[
            Rule.Observable(
                kind="ip",
                value="192.168.0.1",
                relationship="suspicious",
                risk=Rule.Observable.Risk(
                    impact="High",
                    confidence="Medium",
                ),
            ),
            Rule.Observable(
                kind="domain",
                value="malicious.com",
                relationship="malicious",
                risk=Rule.Observable.Risk(
                    impact="Critical",
                    confidence="High",
                ),
            ),
        ],
        output=Rule.Output(
            summary="Unauthorized access detected from multiple sources.",
            context={"alert": "Multiple failed logins", "severity": "high"},
        ),
        collate=Rule.Collate(
            collate_on=["ip", "user_id"],
            within="1h",
            action="append",
        ),
        status=ResourceStatus(
            job_id=101,
            job_name="rule_evaluation_job",
            enabled=True,
            notebook_path="/rules/evaluate_rule.ipynb",
            created_at=datetime(2023, 1, 5, 12, 0),
            job_status="scheduled",
            events=[
                ResourceStatus.StatusEvent(
                    action="create",
                    message="Rule evaluation started",
                    recorded_at=datetime(2023, 1, 5, 12, 0),
                ),
                ResourceStatus.StatusEvent(
                    action="update",
                    message="Rule evaluation finished",
                    recorded_at=datetime(2023, 1, 5, 12, 15),
                ),
            ],
        ),
    )

    assert rule == Rule.from_api_obj(rule.to_api_obj())


def test_transform_request_marshal_unmarshal():
    request = TransformRequest(
        input=TransformRequest.Input(
            columns=[
                Dbui.TableColumnDetails(
                    name="col1",
                    type_name="int",
                    type_detail="integer",
                    position=1,
                    nullable=False,
                ),
                Dbui.TableColumnDetails(
                    name="col2",
                    type_name="varchar",
                    type_detail="string",
                    position=2,
                    nullable=True,
                ),
            ],
            data=[{"col1": "1", "col2": "a"}, {"col1": "2", "col2": "b"}],
        ),
        autoloader_input=TransformRequest.Autoloader(
            format="csv",
            location="s3://bucket/data",
            schema_file="schema.json",
            cloud_files=TransformRequest.Autoloader.CloudFiles(
                schema_hints_file="hints_file.csv", schema_hints="hint1, hint2"
            ),
            row_count=1,
            row_offset=5,
        ),
        use_preset="preset_value",
        transforms=[
            TransformRequest.Transform(
                transform_type="Gold",
                use_preset_table="table_name",
                filter="col > 0",
                post_filter="col < 100",
                preset_overrides=TransformRequest.Transform.PresetOverrides(
                    omit_fields=["field1", "field2"]
                ),
                add_fields=[
                    FieldSpec(
                        name="field1",
                        comment="comment1",
                        var_assert=[
                            FieldSpec.Assert(expr="1=1", message="assertion passed"),
                            FieldSpec.Assert(expr="2=2", message="assertion passed 2"),
                        ],
                        var_from="source_field1",
                        alias="alias1",
                        expr="expr1",
                        literal="literal1",
                        join=FieldSpec.Join(
                            with_table="table_join1",
                            with_csv=FieldSpec.Join.WithCSV(path="csv_path1"),
                            lhs="left1",
                            rhs="right1",
                            select="select_expr1",
                        ),
                    ),
                    FieldSpec(
                        name="field2",
                        comment="comment2",
                        var_assert=[
                            FieldSpec.Assert(expr="a=b", message="assertion ok"),
                            FieldSpec.Assert(expr="c=d", message="assertion ok 2"),
                        ],
                        var_from="source_field2",
                        alias="alias2",
                        expr="expr2",
                        literal="literal2",
                        join=FieldSpec.Join(
                            with_table="table_join2",
                            with_csv=FieldSpec.Join.WithCSV(path="csv_path2"),
                            lhs="left2",
                            rhs="right2",
                            select="select_expr2",
                        ),
                    ),
                ],
                utils=FieldUtils(
                    unreferenced_columns=FieldUtils.UnreferencedColumns(
                        preserve=True,
                        embed_column="all_data",
                        omit_columns=["omit1", "omit2"],
                        duplicate_prefix="dup_",
                    ),
                    json_extract=[
                        FieldUtils.JsonExtract(
                            source="json_column1",
                            omit_fields=["omitA", "omitB"],
                            duplicate_prefix="dup1",
                            embed_column="embed1",
                        ),
                        FieldUtils.JsonExtract(
                            source="json_column2",
                            omit_fields=["omitC", "omitD"],
                            duplicate_prefix="dup2",
                            embed_column="embed2",
                        ),
                    ],
                ),
            ),
            TransformRequest.Transform(
                transform_type="SilverTransform",
                use_preset_table="table_b",
                filter="col >= 10",
                post_filter="col <= 50",
                preset_overrides=TransformRequest.Transform.PresetOverrides(
                    omit_fields=["fieldX", "fieldY"]
                ),
                add_fields=[
                    FieldSpec(
                        name="field3",
                        comment="comment3",
                        var_assert=[
                            FieldSpec.Assert(expr="assert_expr3a", message="message3a"),
                            FieldSpec.Assert(expr="assert_expr3b", message="message3b"),
                        ],
                        var_from="source_field3",
                        alias="alias3",
                        expr="expr3",
                        literal="literal3",
                        join=FieldSpec.Join(
                            with_table="table_join3",
                            with_csv=FieldSpec.Join.WithCSV(path="csv_path3"),
                            lhs="left3",
                            rhs="right3",
                            select="select_expr3",
                        ),
                    ),
                    FieldSpec(
                        name="field4",
                        comment="comment4",
                        var_assert=[
                            FieldSpec.Assert(expr="assert_expr4a", message="message4a"),
                            FieldSpec.Assert(expr="assert_expr4b", message="message4b"),
                        ],
                        var_from="source_field4",
                        alias="alias4",
                        expr="expr4",
                        literal="literal4",
                        join=FieldSpec.Join(
                            with_table="table_join4",
                            with_csv=FieldSpec.Join.WithCSV(path="csv_path4"),
                            lhs="left4",
                            rhs="right4",
                            select="select_expr4",
                        ),
                    ),
                ],
                utils=FieldUtils(
                    unreferenced_columns=FieldUtils.UnreferencedColumns(
                        preserve=False,
                        embed_column="extra_data",
                        omit_columns=["omitX", "omitY", "omitZ"],
                        duplicate_prefix="dupB",
                    ),
                    json_extract=[
                        FieldUtils.JsonExtract(
                            source="json_column3",
                            omit_fields=["omitE", "omitF"],
                            duplicate_prefix="dup3",
                            embed_column="embed3",
                        ),
                        FieldUtils.JsonExtract(
                            source="json_column4",
                            omit_fields=["omitG", "omitH"],
                            duplicate_prefix="dup4",
                            embed_column="embed4",
                        ),
                    ],
                ),
            ),
        ],
    )

    assert request == TransformRequest.from_api_obj(request.to_api_obj())


def test_transform_response_marshal_unmarshal():
    response = TransformResponse(
        stages=[
            TransformResponse.Stages(
                transform_type="Gold",
                columns=[
                    Dbui.TableColumnDetails(
                        name="id",
                        type_name="int",
                        type_detail="integer",
                        position=1,
                        nullable=False,
                    ),
                    Dbui.TableColumnDetails(
                        name="name",
                        type_name="varchar",
                        type_detail="text",
                        position=2,
                        nullable=True,
                    ),
                ],
                data=[{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}],
            ),
            TransformResponse.Stages(
                transform_type="SilverPreTransform",
                columns=[
                    Dbui.TableColumnDetails(
                        name="price",
                        type_name="float",
                        type_detail="decimal",
                        position=3,
                        nullable=False,
                    ),
                    Dbui.TableColumnDetails(
                        name="quantity",
                        type_name="int",
                        type_detail="integer",
                        position=4,
                        nullable=True,
                    ),
                ],
                data=[
                    {"price": "9.99", "quantity": "5"},
                    {"price": "19.99", "quantity": "10"},
                ],
            ),
        ]
    )

    assert response == TransformResponse.from_api_obj(response.to_api_obj())
