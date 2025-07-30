from typing import Optional, List, Dict
from pydantic import BaseModel

from dasl_api import (
    ContentV1PresetDataSourceList,
    ContentV1PresetDataSourceListItemsInner,
    ContentV1DatasourcePresetAutoloader,
    ContentV1DatasourcePresetSilver,
    ContentV1DatasourcePresetSilverPreTransformInner,
    ContentV1DatasourcePresetSilverTransformInner,
    ContentV1DatasourcePresetGoldInner,
    ContentV1DatasourcePreset,
    ContentV1DatasourcePresetAutoloaderCloudFiles,
)

from .datasource import DataSource, FieldSpec, FieldUtils
from .helpers import Helpers


class SilverPreset(BaseModel):
    class PreTransform(BaseModel):
        name: Optional[str] = None
        filter: Optional[str] = None
        post_filter: Optional[str] = None
        fields: Optional[List[Optional[FieldSpec]]] = None
        utils: Optional[FieldUtils] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[ContentV1DatasourcePresetSilverPreTransformInner],
        ) -> Optional["SilverPreset.PreTransform"]:
            if obj is None:
                return None
            if obj.fields is not None:
                fields = [FieldSpec.from_api_obj(item) for item in obj.fields]
            else:
                fields = None

            return SilverPreset.PreTransform(
                name=obj.name,
                filter=obj.filter,
                post_filter=obj.post_filter,
                fields=fields,
                utils=FieldUtils.from_api_obj(obj.utils),
            )

    class Transform(BaseModel):
        name: Optional[str] = None
        filter: Optional[str] = None
        post_filter: Optional[str] = None
        fields: Optional[List[Optional[FieldSpec]]] = None
        utils: Optional[FieldUtils] = None

        @staticmethod
        def from_api_obj(
            obj: Optional[ContentV1DatasourcePresetSilverTransformInner],
        ) -> Optional["SilverPreset.Transform"]:
            if obj is None:
                return None
            if obj.fields is not None:
                fields = [FieldSpec.from_api_obj(item) for item in obj.fields]
            else:
                fields = None

            return SilverPreset.Transform(
                name=obj.name,
                filter=obj.filter,
                post_filter=obj.post_filter,
                fields=fields,
                utils=FieldUtils.from_api_obj(obj.utils),
            )

    pre_transform: Optional[List[PreTransform]] = None
    transform: Optional[List[Transform]] = None

    @staticmethod
    def from_api_obj(
        obj: Optional[ContentV1DatasourcePresetSilver],
    ) -> Optional["SilverPreset"]:
        if obj is None:
            return None

        if obj.pre_transform is not None:
            pre_transform = [
                SilverPreset.PreTransform.from_api_obj(item)
                for item in obj.pre_transform
            ]
        else:
            pre_transform = None

        if obj.transform is not None:
            transform = [
                SilverPreset.Transform.from_api_obj(item) for item in obj.transform
            ]
        else:
            transform = None

        return SilverPreset(
            pre_transform=pre_transform,
            transform=transform,
        )


class GoldPreset(BaseModel):
    name: str
    input: str
    filter: Optional[str] = None
    post_filter: Optional[str] = None
    fields: Optional[List[Optional[FieldSpec]]] = None

    @staticmethod
    def from_api_obj(
        obj: Optional[ContentV1DatasourcePresetGoldInner],
    ) -> Optional["GoldPreset"]:
        if obj is None:
            return None
        if obj.fields is not None:
            fields = [FieldSpec.from_api_obj(item) for item in obj.fields]
        else:
            fields = None

        return GoldPreset(
            name=obj.name,
            input=obj.input,
            filter=obj.filter,
            post_filter=obj.post_filter,
            fields=fields,
        )


class PresetCloudFiles(BaseModel):
    schema_hints_file: Optional[str] = None
    schema_hints: Optional[str] = None

    @staticmethod
    def from_api_obj(
        obj: Optional[ContentV1DatasourcePresetAutoloaderCloudFiles],
    ) -> Optional["PresetCloudFiles"]:
        if obj is None:
            return None

        return PresetCloudFiles(
            schema_hints_file=obj.schema_hints_file,
            schema_hints=obj.schema_hints,
        )


class PresetAutoloader(BaseModel):
    format: str
    schema_file: Optional[str] = None
    var_schema: Optional[str] = None
    cloud_files: Optional[PresetCloudFiles] = None

    @staticmethod
    def from_api_obj(
        obj: Optional[ContentV1DatasourcePresetAutoloader],
    ) -> Optional["PresetAutoloader"]:
        if obj is None:
            return None

        return PresetAutoloader(
            format=obj.format,
            schema_file=obj.schema_file,
            var_schema=obj.var_schema,
            cloud_files=PresetCloudFiles.from_api_obj(obj.cloud_files),
        )


class DataSourcePreset(BaseModel):

    name: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None
    icon_url: Optional[str] = None
    autoloader: Optional[PresetAutoloader] = None
    silver: Optional[SilverPreset] = None
    gold: Optional[List[GoldPreset]] = None

    @staticmethod
    def from_api_obj(
        obj: Optional[ContentV1DatasourcePreset],
    ) -> Optional["DataSourcePreset"]:
        if obj is None:
            return None

        return DataSourcePreset(
            name=obj.name,
            author=obj.author,
            description=obj.description,
            title=obj.title,
            icon_url=obj.icon_url,
            autoloader=PresetAutoloader.from_api_obj(obj.autoloader),
            silver=SilverPreset.from_api_obj(obj.silver),
            gold=[GoldPreset.from_api_obj(item) for item in obj.gold],
        )


class DataSourcePresetSummary(BaseModel):
    name: Optional[str] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    description: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    icon_url: Optional[str] = None

    @staticmethod
    def from_api_obj(
        obj: Optional[ContentV1PresetDataSourceListItemsInner],
    ) -> Optional["DataSourcePresetSummary"]:
        if obj is None:
            return None

        return DataSourcePresetSummary(
            name=obj.name,
            source=obj.source,
            source_type=obj.source_type,
            description=obj.description,
            title=obj.title,
            author=obj.author,
            icon_url=obj.icon_url,
        )


class DataSourcePresetsList(BaseModel):
    kind: Optional[str] = None
    cursor: Optional[str] = None
    items: List["DataSourcePresetSummary"] = []

    @staticmethod
    def from_api_obj(
        obj: Optional[ContentV1PresetDataSourceList],
    ) -> Optional["DataSourcePresetsList"]:
        if obj is None:
            return None
        cursor = None
        if obj.metadata is not None:
            cursor = obj.metadata.cursor

        return DataSourcePresetsList(
            kind=obj.kind,
            cursor=cursor,
            items=[DataSourcePresetSummary.from_api_obj(item) for item in obj.items],
        )
