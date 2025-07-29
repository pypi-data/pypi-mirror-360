r'''
# Amazon S3 Tables Construct Library

<!--BEGIN STABILITY BANNER-->---


![cdk-constructs: Experimental](https://img.shields.io/badge/cdk--constructs-experimental-important.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are experimental and under active development.
> They are subject to non-backward compatible changes or removal in any future version. These are
> not subject to the [Semantic Versioning](https://semver.org/) model and breaking changes will be
> announced in the release notes. This means that while you may use them, you may need to update
> your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

## Amazon S3 Tables

Amazon S3 Tables deliver the first cloud object store with built-in Apache Iceberg support and streamline storing tabular data at scale.

[Product Page](https://aws.amazon.com/s3/features/tables/) | [User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html)

## Usage

### Define an S3 Table Bucket

```python
# Build a Table bucket
sample_table_bucket = TableBucket(scope, "ExampleTableBucket",
    table_bucket_name="example-bucket-1",
    # optional fields:
    unreferenced_file_removal=UnreferencedFileRemoval(
        status=UnreferencedFileRemovalStatus.ENABLED,
        noncurrent_days=20,
        unreferenced_days=20
    )
)
```

Learn more about table buckets maintenance operations and default behavior from the [S3 Tables User Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-table-buckets-maintenance.html)

### Controlling Table Bucket Permissions

```python
# Grant the principal read permissions to the bucket and all tables within
account_id = "123456789012"
table_bucket.grant_read(iam.AccountPrincipal(account_id), "*")

# Grant the role write permissions to the bucket and all tables within
role = iam.Role(stack, "MyRole", assumed_by=iam.ServicePrincipal("sample"))
table_bucket.grant_write(role, "*")

# Grant the user read and write permissions to the bucket and all tables within
table_bucket.grant_read_write(iam.User(stack, "MyUser"), "*")

# Grant permissions to the bucket and a particular table within it
table_id = "6ba046b2-26de-44cf-9144-0c7862593a7b"
table_bucket.grant_read_write(iam.AccountPrincipal(account_id), table_id)

# Add custom resource policy statements
permissions = iam.PolicyStatement(
    effect=iam.Effect.ALLOW,
    actions=["s3tables:*"],
    principals=[iam.ServicePrincipal("example.aws.internal")],
    resources=["*"]
)

table_bucket.add_to_resource_policy(permissions)
```

### Controlling Table Bucket Encryption Settings

S3 TableBuckets have SSE (server-side encryption with AES-256) enabled by default with S3 managed keys.
You can also bring your own KMS key for KMS-SSE or have S3 create a KMS key for you.

If a bucket is encrypted with KMS, grant functions on the bucket will also grant access
to the TableBucket's associated KMS key.

```python
# Provide a user defined KMS Key:
key = kms.Key(scope, "UserKey")
encrypted_bucket = TableBucket(scope, "EncryptedTableBucket",
    table_bucket_name="table-bucket-1",
    encryption=TableBucketEncryption.KMS,
    encryption_key=key
)
# This account principal will also receive kms:Decrypt access to the KMS key
encrypted_bucket.grant_read(iam.AccountPrincipal("123456789012"), "*")

# Use S3 managed server side encryption (default)
encrypted_bucket_default = TableBucket(scope, "EncryptedTableBucketDefault",
    table_bucket_name="table-bucket-3",
    encryption=TableBucketEncryption.S3_MANAGED
)
```

When using KMS encryption (`TableBucketEncryption.KMS`), if no encryption key is provided, CDK will automatically create a new KMS key for the table bucket with necessary permissions.

```python
# If no key is provided, one will be created automatically
encrypted_bucket_auto = TableBucket(scope, "EncryptedTableBucketAuto",
    table_bucket_name="table-bucket-2",
    encryption=TableBucketEncryption.KMS
)
```

## Coming Soon

L2 Construct support for:

* Namespaces
* Tables
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.interface(jsii_type="@aws-cdk/aws-s3tables-alpha.ITableBucket")
class ITableBucket(_aws_cdk_ceddda9d.IResource, typing_extensions.Protocol):
    '''(experimental) Interface definition for S3 Table Buckets.

    :stability: experimental
    '''

    @builtins.property
    @jsii.member(jsii_name="tableBucketArn")
    def table_bucket_arn(self) -> builtins.str:
        '''(experimental) The ARN of the table bucket.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="tableBucketName")
    def table_bucket_name(self) -> builtins.str:
        '''(experimental) The name of the table bucket.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> typing.Optional[builtins.str]:
        '''(experimental) The accountId containing the table bucket.

        :stability: experimental
        :attribute: true
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional KMS encryption key associated with this table bucket.

        :stability: experimental
        '''
        ...

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region containing the table bucket.

        :stability: experimental
        :attribute: true
        '''
        ...

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''(experimental) Adds a statement to the resource policy for a principal (i.e. account/role/service) to perform actions on this table bucket and/or its tables.

        Note that the policy statement may or may not be added to the policy.
        For example, when an ``ITableBucket`` is created from an existing table bucket,
        it's not possible to tell whether the bucket already has a policy
        attached, let alone to re-use that policy to add more statements to it.
        So it's safest to do nothing in these cases.

        :param statement: the policy statement to be added to the bucket's policy.

        :return:

        metadata about the execution of this method. If the policy
        was not added, the value of ``statementAdded`` will be ``false``. You
        should always check this value to make sure that the operation was
        actually carried out. Otherwise, synthesis and deploy will terminate
        silently, which may be confusing.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to decrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: The principal to allow read permissions to.
        :param table_id: Allow the permissions to all tables using '*' or to single table by its unique ID.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantReadWrite")
    def grant_read_write(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read and write permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to encrypt/decrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: The principal to allow read and write permissions to.
        :param table_id: Allow the permissions to all tables using '*' or to single table by its unique ID.

        :stability: experimental
        '''
        ...

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant write permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to encrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: The principal to allow write permissions to.
        :param table_id: Allow the permissions to all tables using '*' or to single table by its unique ID.

        :stability: experimental
        '''
        ...


class _ITableBucketProxy(
    jsii.proxy_for(_aws_cdk_ceddda9d.IResource), # type: ignore[misc]
):
    '''(experimental) Interface definition for S3 Table Buckets.

    :stability: experimental
    '''

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-s3tables-alpha.ITableBucket"

    @builtins.property
    @jsii.member(jsii_name="tableBucketArn")
    def table_bucket_arn(self) -> builtins.str:
        '''(experimental) The ARN of the table bucket.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableBucketArn"))

    @builtins.property
    @jsii.member(jsii_name="tableBucketName")
    def table_bucket_name(self) -> builtins.str:
        '''(experimental) The name of the table bucket.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableBucketName"))

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> typing.Optional[builtins.str]:
        '''(experimental) The accountId containing the table bucket.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "account"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional KMS encryption key associated with this table bucket.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) The region containing the table bucket.

        :stability: experimental
        :attribute: true
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''(experimental) Adds a statement to the resource policy for a principal (i.e. account/role/service) to perform actions on this table bucket and/or its tables.

        Note that the policy statement may or may not be added to the policy.
        For example, when an ``ITableBucket`` is created from an existing table bucket,
        it's not possible to tell whether the bucket already has a policy
        attached, let alone to re-use that policy to add more statements to it.
        So it's safest to do nothing in these cases.

        :param statement: the policy statement to be added to the bucket's policy.

        :return:

        metadata about the execution of this method. If the policy
        was not added, the value of ``statementAdded`` will be ``false``. You
        should always check this value to make sure that the operation was
        actually carried out. Otherwise, synthesis and deploy will terminate
        silently, which may be confusing.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7c10542c60e15926bb4ef59925c4f6c0878400e041897780edddaa65054d627)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to decrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: The principal to allow read permissions to.
        :param table_id: Allow the permissions to all tables using '*' or to single table by its unique ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__853d3e698d103ae1fe304d2239745ee798278fcd22f673c7ae8e9b33884c90a9)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument table_id", value=table_id, expected_type=type_hints["table_id"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [identity, table_id]))

    @jsii.member(jsii_name="grantReadWrite")
    def grant_read_write(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read and write permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to encrypt/decrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: The principal to allow read and write permissions to.
        :param table_id: Allow the permissions to all tables using '*' or to single table by its unique ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c9eb5186509f26b2c015223d6e2614c16cc34d5c2608ca3903b133360e23990)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument table_id", value=table_id, expected_type=type_hints["table_id"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantReadWrite", [identity, table_id]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant write permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to encrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: The principal to allow write permissions to.
        :param table_id: Allow the permissions to all tables using '*' or to single table by its unique ID.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65fa831e505e76e1fe23a8a8d8ce97bb97ebff683edbf67f37020df64c040fdb)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument table_id", value=table_id, expected_type=type_hints["table_id"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantWrite", [identity, table_id]))

# Adding a "__jsii_proxy_class__(): typing.Type" function to the interface
typing.cast(typing.Any, ITableBucket).__jsii_proxy_class__ = lambda : _ITableBucketProxy


@jsii.implements(ITableBucket)
class TableBucket(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-s3tables-alpha.TableBucket",
):
    '''(experimental) An S3 table bucket with helpers for associated resource policies.

    This bucket may not yet have all features that exposed by the underlying CfnTableBucket.

    :stability: experimental
    :stateful: true

    Example::

        sample_table_bucket = TableBucket(scope, "ExampleTableBucket",
            table_bucket_name="example-bucket",
            # Optional fields:
            unreferenced_file_removal=UnreferencedFileRemoval(
                noncurrent_days=123,
                status=UnreferencedFileRemovalStatus.ENABLED,
                unreferenced_days=123
            )
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        table_bucket_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        encryption: typing.Optional["TableBucketEncryption"] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        region: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        unreferenced_file_removal: typing.Optional[typing.Union["UnreferencedFileRemoval", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param table_bucket_name: (experimental) Name of the S3 TableBucket.
        :param account: (experimental) AWS Account ID of the table bucket owner. Default: - it's assumed the bucket belongs to the same account as the scope it's being imported into
        :param encryption: (experimental) The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        :param encryption_key: (experimental) External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS``. An error will be emitted if ``encryption`` is set to ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param region: (experimental) AWS region that the table bucket exists in. Default: - it's assumed the bucket is in the same region as the scope it's being imported into
        :param removal_policy: (experimental) Controls what happens to this table bucket it it stoped being managed by cloudformation. Default: RETAIN
        :param unreferenced_file_removal: (experimental) Unreferenced file removal settings for the S3 TableBucket. Default: Enabled with default values

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d9c0bf5c954c2a6797301b7dc6cb8abd812336f3507addc92f72b805ec0a1e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TableBucketProps(
            table_bucket_name=table_bucket_name,
            account=account,
            encryption=encryption,
            encryption_key=encryption_key,
            region=region,
            removal_policy=removal_policy,
            unreferenced_file_removal=unreferenced_file_removal,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="fromTableBucketArn")
    @builtins.classmethod
    def from_table_bucket_arn(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        table_bucket_arn: builtins.str,
    ) -> ITableBucket:
        '''(experimental) Defines a TableBucket construct from an external table bucket ARN.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param table_bucket_arn: Amazon Resource Name (arn) of the table bucket.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03d844a802df53acfc8906e32d1d2bbab0d86fedd5fc2ef65296a8c7a0c368d5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument table_bucket_arn", value=table_bucket_arn, expected_type=type_hints["table_bucket_arn"])
        return typing.cast(ITableBucket, jsii.sinvoke(cls, "fromTableBucketArn", [scope, id, table_bucket_arn]))

    @jsii.member(jsii_name="fromTableBucketAttributes")
    @builtins.classmethod
    def from_table_bucket_attributes(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        account: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        region: typing.Optional[builtins.str] = None,
        table_bucket_arn: typing.Optional[builtins.str] = None,
        table_bucket_name: typing.Optional[builtins.str] = None,
    ) -> ITableBucket:
        '''(experimental) Defines a TableBucket construct that represents an external table bucket.

        :param scope: The parent creating construct (usually ``this``).
        :param id: The construct's name.
        :param account: (experimental) The accountId containing this table bucket. Default: account inferred from scope
        :param encryption_key: (experimental) Optional KMS encryption key associated with this bucket. Default: - undefined
        :param region: (experimental) AWS region this table bucket exists in. Default: region inferred from scope
        :param table_bucket_arn: (experimental) The table bucket's ARN. Default: tableBucketArn constructed from region, account and tableBucketName are provided
        :param table_bucket_name: (experimental) The table bucket name, unique per region. Default: tableBucketName inferred from arn

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fd93d11fc9c336a7e785b6aaa945ba1d55d75eb3748b03a2030b08e3d152961)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        attrs = TableBucketAttributes(
            account=account,
            encryption_key=encryption_key,
            region=region,
            table_bucket_arn=table_bucket_arn,
            table_bucket_name=table_bucket_name,
        )

        return typing.cast(ITableBucket, jsii.sinvoke(cls, "fromTableBucketAttributes", [scope, id, attrs]))

    @jsii.member(jsii_name="validateTableBucketName")
    @builtins.classmethod
    def validate_table_bucket_name(
        cls,
        bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) Throws an exception if the given table bucket name is not valid.

        :param bucket_name: name of the bucket.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__054bf3ff46c98611841750ec27c0d492c7ee0aa6480b03f4a250c1d73bf049f7)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
        return typing.cast(None, jsii.sinvoke(cls, "validateTableBucketName", [bucket_name]))

    @jsii.member(jsii_name="validateUnreferencedFileRemoval")
    @builtins.classmethod
    def validate_unreferenced_file_removal(
        cls,
        *,
        noncurrent_days: typing.Optional[jsii.Number] = None,
        status: typing.Optional["UnreferencedFileRemovalStatus"] = None,
        unreferenced_days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Throws an exception if the given unreferencedFileRemovalProperty is not valid.

        :param noncurrent_days: (experimental) Duration after which noncurrent files should be removed. Should be at least one day. Default: - See S3 Tables User Guide
        :param status: (experimental) Status of unreferenced file removal. Can be Enabled or Disabled. Default: - See S3 Tables User Guide
        :param unreferenced_days: (experimental) Duration after which unreferenced files should be removed. Should be at least one day. Default: - See S3 Tables User Guide

        :stability: experimental
        '''
        unreferenced_file_removal = UnreferencedFileRemoval(
            noncurrent_days=noncurrent_days,
            status=status,
            unreferenced_days=unreferenced_days,
        )

        return typing.cast(None, jsii.sinvoke(cls, "validateUnreferencedFileRemoval", [unreferenced_file_removal]))

    @jsii.member(jsii_name="addToResourcePolicy")
    def add_to_resource_policy(
        self,
        statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> _aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult:
        '''(experimental) Adds a statement to the resource policy for a principal (i.e. account/role/service) to perform actions on this table bucket and/or its contents. Use ``tableBucketArn`` and ``arnForObjects(keys)`` to obtain ARNs for this bucket or objects.

        Note that the policy statement may or may not be added to the policy.
        For example, when an ``ITableBucket`` is created from an existing table bucket,
        it's not possible to tell whether the bucket already has a policy
        attached, let alone to re-use that policy to add more statements to it.
        So it's safest to do nothing in these cases.

        :param statement: the policy statement to be added to the bucket's policy.

        :return:

        metadata about the execution of this method. If the policy
        was not added, the value of ``statementAdded`` will be ``false``. You
        should always check this value to make sure that the operation was
        actually carried out. Otherwise, synthesis and deploy will terminate
        silently, which may be confusing.

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51cd52e5dbcb37ec9f9fd146daf9705f341ba8056f0f9d812355dc6e0ec273cd)
            check_type(argname="argument statement", value=statement, expected_type=type_hints["statement"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.AddToResourcePolicyResult, jsii.invoke(self, "addToResourcePolicy", [statement]))

    @jsii.member(jsii_name="grantRead")
    def grant_read(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to decrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: -
        :param table_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fecb8141f36793842f11c48ee39490301f24e6f1f0de09abbbf16bf1f96f0cb3)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument table_id", value=table_id, expected_type=type_hints["table_id"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantRead", [identity, table_id]))

    @jsii.member(jsii_name="grantReadWrite")
    def grant_read_write(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant read and write permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to encrypt/decrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: -
        :param table_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd8d4708cc079743c68f1ed7c239ba7a268460ad7ce4e417684326708cd34a54)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument table_id", value=table_id, expected_type=type_hints["table_id"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantReadWrite", [identity, table_id]))

    @jsii.member(jsii_name="grantWrite")
    def grant_write(
        self,
        identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
        table_id: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.Grant:
        '''(experimental) Grant write permissions for this table bucket and its tables to an IAM principal (Role/Group/User).

        If encryption is used, permission to use the key to encrypt the contents
        of the bucket will also be granted to the same principal.

        :param identity: -
        :param table_id: -

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f9476ce4489c94b0b073d56ebee26cf1a8f5db20184e82de18e7238c0381b9a)
            check_type(argname="argument identity", value=identity, expected_type=type_hints["identity"])
            check_type(argname="argument table_id", value=table_id, expected_type=type_hints["table_id"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.Grant, jsii.invoke(self, "grantWrite", [identity, table_id]))

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="tableBucketArn")
    def table_bucket_arn(self) -> builtins.str:
        '''(experimental) The unique Amazon Resource Name (arn) of this table bucket.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableBucketArn"))

    @builtins.property
    @jsii.member(jsii_name="tableBucketName")
    def table_bucket_name(self) -> builtins.str:
        '''(experimental) The name of this table bucket.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.get(self, "tableBucketName"))

    @builtins.property
    @jsii.member(jsii_name="encryptionKey")
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional KMS encryption key associated with this table bucket.

        :stability: experimental
        '''
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], jsii.get(self, "encryptionKey"))

    @builtins.property
    @jsii.member(jsii_name="tableBucketPolicy")
    def table_bucket_policy(self) -> typing.Optional["TableBucketPolicy"]:
        '''(experimental) The resource policy for this tableBucket.

        :stability: experimental
        '''
        return typing.cast(typing.Optional["TableBucketPolicy"], jsii.get(self, "tableBucketPolicy"))

    @builtins.property
    @jsii.member(jsii_name="autoCreatePolicy")
    def _auto_create_policy(self) -> builtins.bool:
        '''(experimental) Indicates if a table bucket resource policy should automatically created upon the first call to ``addToResourcePolicy``.

        :stability: experimental
        '''
        return typing.cast(builtins.bool, jsii.get(self, "autoCreatePolicy"))

    @_auto_create_policy.setter
    def _auto_create_policy(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddda0c30ebb465614a7378f709964b48c9f175013aa1ed12f0ea7c1218e8c630)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoCreatePolicy", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@aws-cdk/aws-s3tables-alpha.TableBucketAttributes",
    jsii_struct_bases=[],
    name_mapping={
        "account": "account",
        "encryption_key": "encryptionKey",
        "region": "region",
        "table_bucket_arn": "tableBucketArn",
        "table_bucket_name": "tableBucketName",
    },
)
class TableBucketAttributes:
    def __init__(
        self,
        *,
        account: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        region: typing.Optional[builtins.str] = None,
        table_bucket_arn: typing.Optional[builtins.str] = None,
        table_bucket_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''(experimental) A reference to a table bucket outside this stack.

        The tableBucketName, region, and account can be provided explicitly
        or will be inferred from the tableBucketArn

        :param account: (experimental) The accountId containing this table bucket. Default: account inferred from scope
        :param encryption_key: (experimental) Optional KMS encryption key associated with this bucket. Default: - undefined
        :param region: (experimental) AWS region this table bucket exists in. Default: region inferred from scope
        :param table_bucket_arn: (experimental) The table bucket's ARN. Default: tableBucketArn constructed from region, account and tableBucketName are provided
        :param table_bucket_name: (experimental) The table bucket name, unique per region. Default: tableBucketName inferred from arn

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_s3tables_alpha as s3tables_alpha
            from aws_cdk import aws_kms as kms
            
            # key: kms.Key
            
            table_bucket_attributes = s3tables_alpha.TableBucketAttributes(
                account="account",
                encryption_key=key,
                region="region",
                table_bucket_arn="tableBucketArn",
                table_bucket_name="tableBucketName"
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f628073bbee2e81e2162c5225d2230a24b470a8915e2ee4cef917951de644d61)
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument table_bucket_arn", value=table_bucket_arn, expected_type=type_hints["table_bucket_arn"])
            check_type(argname="argument table_bucket_name", value=table_bucket_name, expected_type=type_hints["table_bucket_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if account is not None:
            self._values["account"] = account
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if region is not None:
            self._values["region"] = region
        if table_bucket_arn is not None:
            self._values["table_bucket_arn"] = table_bucket_arn
        if table_bucket_name is not None:
            self._values["table_bucket_name"] = table_bucket_name

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''(experimental) The accountId containing this table bucket.

        :default: account inferred from scope

        :stability: experimental
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) Optional KMS encryption key associated with this bucket.

        :default: - undefined

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) AWS region this table bucket exists in.

        :default: region inferred from scope

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_bucket_arn(self) -> typing.Optional[builtins.str]:
        '''(experimental) The table bucket's ARN.

        :default: tableBucketArn constructed from region, account and tableBucketName are provided

        :stability: experimental
        '''
        result = self._values.get("table_bucket_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def table_bucket_name(self) -> typing.Optional[builtins.str]:
        '''(experimental) The table bucket name, unique per region.

        :default: tableBucketName inferred from arn

        :stability: experimental
        '''
        result = self._values.get("table_bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TableBucketAttributes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-s3tables-alpha.TableBucketEncryption")
class TableBucketEncryption(enum.Enum):
    '''(experimental) Controls Server Side Encryption (SSE) for this TableBucket.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Provide a user defined KMS Key:
        key = kms.Key(scope, "UserKey")
        encrypted_bucket = TableBucket(scope, "EncryptedTableBucket",
            table_bucket_name="table-bucket-1",
            encryption=TableBucketEncryption.KMS,
            encryption_key=key
        )
        # This account principal will also receive kms:Decrypt access to the KMS key
        encrypted_bucket.grant_read(iam.AccountPrincipal("123456789012"), "*")
        
        # Use S3 managed server side encryption (default)
        encrypted_bucket_default = TableBucket(scope, "EncryptedTableBucketDefault",
            table_bucket_name="table-bucket-3",
            encryption=TableBucketEncryption.S3_MANAGED
        )
    '''

    KMS = "KMS"
    '''(experimental) Use a customer defined KMS key for encryption If ``encryptionKey`` is specified, this key will be used, otherwise, one will be defined.

    :stability: experimental
    '''
    S3_MANAGED = "S3_MANAGED"
    '''(experimental) Use S3 managed encryption keys with AES256 encryption.

    :stability: experimental
    '''


class TableBucketPolicy(
    _aws_cdk_ceddda9d.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-s3tables-alpha.TableBucketPolicy",
):
    '''(experimental) A Bucket Policy for S3 TableBuckets.

    You will almost never need to use this construct directly.
    Instead, TableBucket.addToResourcePolicy can be used to add more policies to your bucket directly

    :stability: experimental
    :exampleMetadata: fixture=_generated

    Example::

        # The code below shows an example of how to instantiate this type.
        # The values are placeholders you should change.
        import aws_cdk.aws_s3tables_alpha as s3tables_alpha
        import aws_cdk as cdk
        from aws_cdk import aws_iam as iam
        
        # policy_document: iam.PolicyDocument
        # table_bucket: s3tables_alpha.TableBucket
        
        table_bucket_policy = s3tables_alpha.TableBucketPolicy(self, "MyTableBucketPolicy",
            table_bucket=table_bucket,
        
            # the properties below are optional
            removal_policy=cdk.RemovalPolicy.DESTROY,
            resource_policy=policy_document
        )
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        table_bucket: ITableBucket,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        resource_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param table_bucket: (experimental) The associated table bucket.
        :param removal_policy: (experimental) Policy to apply when the policy is removed from this stack. Default: - RemovalPolicy.DESTROY.
        :param resource_policy: (experimental) The policy document for the bucket's resource policy. Default: undefined An empty iam.PolicyDocument will be initialized

        :stability: experimental
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26a65a7f8b5344e57811d88192dc3cf822bfa45031afe03f34576593e271e7b1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = TableBucketPolicyProps(
            table_bucket=table_bucket,
            removal_policy=removal_policy,
            resource_policy=resource_policy,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.python.classproperty
    @jsii.member(jsii_name="PROPERTY_INJECTION_ID")
    def PROPERTY_INJECTION_ID(cls) -> builtins.str:
        '''(experimental) Uniquely identifies this class.

        :stability: experimental
        '''
        return typing.cast(builtins.str, jsii.sget(cls, "PROPERTY_INJECTION_ID"))

    @builtins.property
    @jsii.member(jsii_name="document")
    def document(self) -> _aws_cdk_aws_iam_ceddda9d.PolicyDocument:
        '''(experimental) The IAM PolicyDocument containing permissions represented by this policy.

        :stability: experimental
        '''
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.PolicyDocument, jsii.get(self, "document"))


@jsii.data_type(
    jsii_type="@aws-cdk/aws-s3tables-alpha.TableBucketPolicyProps",
    jsii_struct_bases=[],
    name_mapping={
        "table_bucket": "tableBucket",
        "removal_policy": "removalPolicy",
        "resource_policy": "resourcePolicy",
    },
)
class TableBucketPolicyProps:
    def __init__(
        self,
        *,
        table_bucket: ITableBucket,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        resource_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
    ) -> None:
        '''(experimental) Parameters for constructing a TableBucketPolicy.

        :param table_bucket: (experimental) The associated table bucket.
        :param removal_policy: (experimental) Policy to apply when the policy is removed from this stack. Default: - RemovalPolicy.DESTROY.
        :param resource_policy: (experimental) The policy document for the bucket's resource policy. Default: undefined An empty iam.PolicyDocument will be initialized

        :stability: experimental
        :exampleMetadata: fixture=_generated

        Example::

            # The code below shows an example of how to instantiate this type.
            # The values are placeholders you should change.
            import aws_cdk.aws_s3tables_alpha as s3tables_alpha
            import aws_cdk as cdk
            from aws_cdk import aws_iam as iam
            
            # policy_document: iam.PolicyDocument
            # table_bucket: s3tables_alpha.TableBucket
            
            table_bucket_policy_props = s3tables_alpha.TableBucketPolicyProps(
                table_bucket=table_bucket,
            
                # the properties below are optional
                removal_policy=cdk.RemovalPolicy.DESTROY,
                resource_policy=policy_document
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8afedf0f9c96ed3f2bfa2918ddf62a334b286bd16c0997d1db2f20acd045d28)
            check_type(argname="argument table_bucket", value=table_bucket, expected_type=type_hints["table_bucket"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument resource_policy", value=resource_policy, expected_type=type_hints["resource_policy"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "table_bucket": table_bucket,
        }
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if resource_policy is not None:
            self._values["resource_policy"] = resource_policy

    @builtins.property
    def table_bucket(self) -> ITableBucket:
        '''(experimental) The associated table bucket.

        :stability: experimental
        '''
        result = self._values.get("table_bucket")
        assert result is not None, "Required property 'table_bucket' is missing"
        return typing.cast(ITableBucket, result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) Policy to apply when the policy is removed from this stack.

        :default: - RemovalPolicy.DESTROY.

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def resource_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument]:
        '''(experimental) The policy document for the bucket's resource policy.

        :default: undefined An empty iam.PolicyDocument will be initialized

        :stability: experimental
        '''
        result = self._values.get("resource_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TableBucketPolicyProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-s3tables-alpha.TableBucketProps",
    jsii_struct_bases=[],
    name_mapping={
        "table_bucket_name": "tableBucketName",
        "account": "account",
        "encryption": "encryption",
        "encryption_key": "encryptionKey",
        "region": "region",
        "removal_policy": "removalPolicy",
        "unreferenced_file_removal": "unreferencedFileRemoval",
    },
)
class TableBucketProps:
    def __init__(
        self,
        *,
        table_bucket_name: builtins.str,
        account: typing.Optional[builtins.str] = None,
        encryption: typing.Optional[TableBucketEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        region: typing.Optional[builtins.str] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        unreferenced_file_removal: typing.Optional[typing.Union["UnreferencedFileRemoval", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''(experimental) Parameters for constructing a TableBucket.

        :param table_bucket_name: (experimental) Name of the S3 TableBucket.
        :param account: (experimental) AWS Account ID of the table bucket owner. Default: - it's assumed the bucket belongs to the same account as the scope it's being imported into
        :param encryption: (experimental) The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.
        :param encryption_key: (experimental) External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS``. An error will be emitted if ``encryption`` is set to ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param region: (experimental) AWS region that the table bucket exists in. Default: - it's assumed the bucket is in the same region as the scope it's being imported into
        :param removal_policy: (experimental) Controls what happens to this table bucket it it stoped being managed by cloudformation. Default: RETAIN
        :param unreferenced_file_removal: (experimental) Unreferenced file removal settings for the S3 TableBucket. Default: Enabled with default values

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Build a Table bucket
            sample_table_bucket = TableBucket(scope, "ExampleTableBucket",
                table_bucket_name="example-bucket-1",
                # optional fields:
                unreferenced_file_removal=UnreferencedFileRemoval(
                    status=UnreferencedFileRemovalStatus.ENABLED,
                    noncurrent_days=20,
                    unreferenced_days=20
                )
            )
        '''
        if isinstance(unreferenced_file_removal, dict):
            unreferenced_file_removal = UnreferencedFileRemoval(**unreferenced_file_removal)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa14ccf904c2576c446af7122d6335d3a92b012274a231120ab28c942832368b)
            check_type(argname="argument table_bucket_name", value=table_bucket_name, expected_type=type_hints["table_bucket_name"])
            check_type(argname="argument account", value=account, expected_type=type_hints["account"])
            check_type(argname="argument encryption", value=encryption, expected_type=type_hints["encryption"])
            check_type(argname="argument encryption_key", value=encryption_key, expected_type=type_hints["encryption_key"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument unreferenced_file_removal", value=unreferenced_file_removal, expected_type=type_hints["unreferenced_file_removal"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "table_bucket_name": table_bucket_name,
        }
        if account is not None:
            self._values["account"] = account
        if encryption is not None:
            self._values["encryption"] = encryption
        if encryption_key is not None:
            self._values["encryption_key"] = encryption_key
        if region is not None:
            self._values["region"] = region
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if unreferenced_file_removal is not None:
            self._values["unreferenced_file_removal"] = unreferenced_file_removal

    @builtins.property
    def table_bucket_name(self) -> builtins.str:
        '''(experimental) Name of the S3 TableBucket.

        :stability: experimental
        :link: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables-buckets-naming.html#table-buckets-naming-rules
        '''
        result = self._values.get("table_bucket_name")
        assert result is not None, "Required property 'table_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def account(self) -> typing.Optional[builtins.str]:
        '''(experimental) AWS Account ID of the table bucket owner.

        :default: - it's assumed the bucket belongs to the same account as the scope it's being imported into

        :stability: experimental
        '''
        result = self._values.get("account")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def encryption(self) -> typing.Optional[TableBucketEncryption]:
        '''(experimental) The kind of server-side encryption to apply to this bucket.

        If you choose KMS, you can specify a KMS key via ``encryptionKey``. If
        encryption key is not specified, a key will automatically be created.

        :default: - ``KMS`` if ``encryptionKey`` is specified, or ``S3_MANAGED`` otherwise.

        :stability: experimental
        '''
        result = self._values.get("encryption")
        return typing.cast(typing.Optional[TableBucketEncryption], result)

    @builtins.property
    def encryption_key(self) -> typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey]:
        '''(experimental) External KMS key to use for bucket encryption.

        The ``encryption`` property must be either not specified or set to ``KMS``.
        An error will be emitted if ``encryption`` is set to ``S3_MANAGED``.

        :default:

        - If ``encryption`` is set to ``KMS`` and this property is undefined,
        a new KMS key will be created and associated with this bucket.

        :stability: experimental
        '''
        result = self._values.get("encryption_key")
        return typing.cast(typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''(experimental) AWS region that the table bucket exists in.

        :default: - it's assumed the bucket is in the same region as the scope it's being imported into

        :stability: experimental
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''(experimental) Controls what happens to this table bucket it it stoped being managed by cloudformation.

        :default: RETAIN

        :stability: experimental
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def unreferenced_file_removal(self) -> typing.Optional["UnreferencedFileRemoval"]:
        '''(experimental) Unreferenced file removal settings for the S3 TableBucket.

        :default: Enabled with default values

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-table-buckets-maintenance.html
        :stability: experimental
        :link: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-s3tables-tablebucket-unreferencedfileremoval.html
        '''
        result = self._values.get("unreferenced_file_removal")
        return typing.cast(typing.Optional["UnreferencedFileRemoval"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TableBucketProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-s3tables-alpha.UnreferencedFileRemoval",
    jsii_struct_bases=[],
    name_mapping={
        "noncurrent_days": "noncurrentDays",
        "status": "status",
        "unreferenced_days": "unreferencedDays",
    },
)
class UnreferencedFileRemoval:
    def __init__(
        self,
        *,
        noncurrent_days: typing.Optional[jsii.Number] = None,
        status: typing.Optional["UnreferencedFileRemovalStatus"] = None,
        unreferenced_days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''(experimental) Unreferenced file removal settings for the this table bucket.

        :param noncurrent_days: (experimental) Duration after which noncurrent files should be removed. Should be at least one day. Default: - See S3 Tables User Guide
        :param status: (experimental) Status of unreferenced file removal. Can be Enabled or Disabled. Default: - See S3 Tables User Guide
        :param unreferenced_days: (experimental) Duration after which unreferenced files should be removed. Should be at least one day. Default: - See S3 Tables User Guide

        :stability: experimental
        :exampleMetadata: infused

        Example::

            # Build a Table bucket
            sample_table_bucket = TableBucket(scope, "ExampleTableBucket",
                table_bucket_name="example-bucket-1",
                # optional fields:
                unreferenced_file_removal=UnreferencedFileRemoval(
                    status=UnreferencedFileRemovalStatus.ENABLED,
                    noncurrent_days=20,
                    unreferenced_days=20
                )
            )
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3c9fa2e0832ae26e721328d6c201e9e86774721d68903a6414d69d8a77a5675)
            check_type(argname="argument noncurrent_days", value=noncurrent_days, expected_type=type_hints["noncurrent_days"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument unreferenced_days", value=unreferenced_days, expected_type=type_hints["unreferenced_days"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if noncurrent_days is not None:
            self._values["noncurrent_days"] = noncurrent_days
        if status is not None:
            self._values["status"] = status
        if unreferenced_days is not None:
            self._values["unreferenced_days"] = unreferenced_days

    @builtins.property
    def noncurrent_days(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Duration after which noncurrent files should be removed.

        Should be at least one day.

        :default: - See S3 Tables User Guide

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-table-buckets-maintenance.html
        :stability: experimental
        '''
        result = self._values.get("noncurrent_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def status(self) -> typing.Optional["UnreferencedFileRemovalStatus"]:
        '''(experimental) Status of unreferenced file removal.

        Can be Enabled or Disabled.

        :default: - See S3 Tables User Guide

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-table-buckets-maintenance.html
        :stability: experimental
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional["UnreferencedFileRemovalStatus"], result)

    @builtins.property
    def unreferenced_days(self) -> typing.Optional[jsii.Number]:
        '''(experimental) Duration after which unreferenced files should be removed.

        Should be at least one day.

        :default: - See S3 Tables User Guide

        :see: https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-table-buckets-maintenance.html
        :stability: experimental
        '''
        result = self._values.get("unreferenced_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "UnreferencedFileRemoval(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@aws-cdk/aws-s3tables-alpha.UnreferencedFileRemovalStatus")
class UnreferencedFileRemovalStatus(enum.Enum):
    '''(experimental) Controls whether unreferenced file removal is enabled or disabled.

    :stability: experimental
    :exampleMetadata: infused

    Example::

        # Build a Table bucket
        sample_table_bucket = TableBucket(scope, "ExampleTableBucket",
            table_bucket_name="example-bucket-1",
            # optional fields:
            unreferenced_file_removal=UnreferencedFileRemoval(
                status=UnreferencedFileRemovalStatus.ENABLED,
                noncurrent_days=20,
                unreferenced_days=20
            )
        )
    '''

    ENABLED = "ENABLED"
    '''(experimental) Enable unreferenced file removal.

    :stability: experimental
    '''
    DISABLED = "DISABLED"
    '''(experimental) Disable unreferenced file removal.

    :stability: experimental
    '''


__all__ = [
    "ITableBucket",
    "TableBucket",
    "TableBucketAttributes",
    "TableBucketEncryption",
    "TableBucketPolicy",
    "TableBucketPolicyProps",
    "TableBucketProps",
    "UnreferencedFileRemoval",
    "UnreferencedFileRemovalStatus",
]

publication.publish()

def _typecheckingstub__a7c10542c60e15926bb4ef59925c4f6c0878400e041897780edddaa65054d627(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__853d3e698d103ae1fe304d2239745ee798278fcd22f673c7ae8e9b33884c90a9(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    table_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c9eb5186509f26b2c015223d6e2614c16cc34d5c2608ca3903b133360e23990(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    table_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65fa831e505e76e1fe23a8a8d8ce97bb97ebff683edbf67f37020df64c040fdb(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    table_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d9c0bf5c954c2a6797301b7dc6cb8abd812336f3507addc92f72b805ec0a1e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    table_bucket_name: builtins.str,
    account: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[TableBucketEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    region: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    unreferenced_file_removal: typing.Optional[typing.Union[UnreferencedFileRemoval, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03d844a802df53acfc8906e32d1d2bbab0d86fedd5fc2ef65296a8c7a0c368d5(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    table_bucket_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fd93d11fc9c336a7e785b6aaa945ba1d55d75eb3748b03a2030b08e3d152961(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    account: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    region: typing.Optional[builtins.str] = None,
    table_bucket_arn: typing.Optional[builtins.str] = None,
    table_bucket_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__054bf3ff46c98611841750ec27c0d492c7ee0aa6480b03f4a250c1d73bf049f7(
    bucket_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51cd52e5dbcb37ec9f9fd146daf9705f341ba8056f0f9d812355dc6e0ec273cd(
    statement: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fecb8141f36793842f11c48ee39490301f24e6f1f0de09abbbf16bf1f96f0cb3(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    table_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd8d4708cc079743c68f1ed7c239ba7a268460ad7ce4e417684326708cd34a54(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    table_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f9476ce4489c94b0b073d56ebee26cf1a8f5db20184e82de18e7238c0381b9a(
    identity: _aws_cdk_aws_iam_ceddda9d.IGrantable,
    table_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddda0c30ebb465614a7378f709964b48c9f175013aa1ed12f0ea7c1218e8c630(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f628073bbee2e81e2162c5225d2230a24b470a8915e2ee4cef917951de644d61(
    *,
    account: typing.Optional[builtins.str] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    region: typing.Optional[builtins.str] = None,
    table_bucket_arn: typing.Optional[builtins.str] = None,
    table_bucket_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26a65a7f8b5344e57811d88192dc3cf822bfa45031afe03f34576593e271e7b1(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    table_bucket: ITableBucket,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    resource_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8afedf0f9c96ed3f2bfa2918ddf62a334b286bd16c0997d1db2f20acd045d28(
    *,
    table_bucket: ITableBucket,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    resource_policy: typing.Optional[_aws_cdk_aws_iam_ceddda9d.PolicyDocument] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa14ccf904c2576c446af7122d6335d3a92b012274a231120ab28c942832368b(
    *,
    table_bucket_name: builtins.str,
    account: typing.Optional[builtins.str] = None,
    encryption: typing.Optional[TableBucketEncryption] = None,
    encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
    region: typing.Optional[builtins.str] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    unreferenced_file_removal: typing.Optional[typing.Union[UnreferencedFileRemoval, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3c9fa2e0832ae26e721328d6c201e9e86774721d68903a6414d69d8a77a5675(
    *,
    noncurrent_days: typing.Optional[jsii.Number] = None,
    status: typing.Optional[UnreferencedFileRemovalStatus] = None,
    unreferenced_days: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
