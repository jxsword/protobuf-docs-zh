+++
title = "Objective-C 生成代码指南"
weight = 710
linkTitle = "生成代码指南"
description = "准确描述 Protobuf 编译器会为任意给定的协议定义生成哪些 Objective-C 代码。"
type = "docs"
source_url = "https://protobuf.dev/reference/objective-c/objective-c-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本文会重点标出 proto2、proto3 与版次（Editions）三者生成代码（generated code）之间的任何差异。在阅读本文档之前，你应当先阅读
[proto2 语言指南（language guide）](/programming-guides/proto2)
和/或
[proto3 语言指南](/programming-guides/proto3)
和/或[版次语言指南](/programming-guides/editions)。

## 编译器调用 {#invocation}

使用 `--objc_out=` 命令行标志调用 Protobuf 编译器时，会生成 Objective-C 输出。`--objc_out=` 选项的参数是你希望编译器写入 Objective-C 输出的目录。编译器会为每个输入的 `.proto` 文件创建一个头文件和一个实现文件。输出文件名的计算方式是：取 `.proto` 文件的名称，并做如下修改：

-   文件名由 `.proto` 文件的基本名转换为驼峰命名（camel case）而得。例如，`foo_bar.proto` 将变为 `FooBar`。
-   扩展名（`.proto`）被替换为 `pbobjc.h` 或 `pbobjc.m`，分别对应头文件或实现文件。
-   proto 路径（通过 `--proto_path=` 或 `-I` 命令行标志指定）被替换为输出路径（通过 `--objc_out=` 标志指定）。

例如，如果你按如下方式调用编译器：

```shell
protoc --proto_path=src --objc_out=build/gen src/foo.proto src/bar/baz.proto
```

编译器会读取 `src/foo.proto` 和 `src/bar/baz.proto` 文件，并生成四个输出文件：`build/gen/Foo.pbobjc.h`、`build/gen/Foo.pbobjc.m`、`build/gen/bar/Baz.pbobjc.h` 和 `build/gen/bar/Baz.pbobjc.m`。如有必要，编译器会自动创建 `build/gen/bar` 目录，但*不会*创建 `build` 或 `build/gen`；这两个目录必须已经存在。

## 包 {#package}

Protobuf 编译器生成的 Objective-C 代码完全不受 `.proto` 文件中定义的包（package）名的影响，因为 Objective-C 没有语言层面的命名空间（namespace）强制机制。作为替代，Objective-C 类名通过前缀来区分，具体内容见下一节。

## 类前缀 {#prefix}

给定如下[文件选项（file option）](/programming-guides/proto3#options)：

```proto
option objc_class_prefix = "CGOOP";
```

指定的字符串——本例中为 `CGOOP`——会作为前缀加在该 `.proto` 文件生成的所有 Objective-C 类名之前。请按 Apple 的建议使用 3 个或更多字符的前缀。注意，所有两个字母的前缀均由 Apple 保留。

## 驼峰命名转换 {#case}

地道的 Objective-C 代码对所有标识符使用驼峰命名。

消息（message）的名称不会被转换，因为 proto 文件的惯例本来就是以驼峰命名来命名消息。这里假定用户是出于正当理由而绕开了这一惯例，实现将遵从其意图。

由字段（field）名和 `oneof`、`enum` 声明以及扩展（extension）访问器（accessor）生成的方法，其名称会被驼峰化。一般来说，从 proto 名称转换为驼峰命名的 Objective-C 名称的规则如下：

-   首字母转换为大写（字段除外，字段总是以小写字母开头）。
-   名称中的每个下划线都会被移除，其后的字母转为大写。

例如，字段 `foo_bar_baz` 变为 `fooBarBaz`。字段 `FOO_bar` 变为 `fooBar`。

## 消息 {#message}

给定如下简单消息声明：

```proto
message Foo {}
```

Protobuf 编译器会生成一个名为 `Foo` 的类。如果你指定了 [`objc_class_prefix` 文件选项](#prefix)，该选项的值会被前置到生成的类名上。

对于名称与任何 C/C++ 或 Objective-C 关键字相同的外层消息：

```proto
message static {}
```

生成的接口会加上 `_Class` 后缀，如下所示：

```objc
@interface static_Class {}
```

注意，根据[驼峰命名转换规则](#case)，名称 `static` *不会*被转换。如果某个内层消息的驼峰命名名称恰为 `FieldNumber` 或 `OneOfCase`，生成的接口会在该驼峰命名名称后加上 `_Class` 后缀，以确保生成的名称不会与 `FieldNumber` 枚举或 `OneOfCase` 枚举冲突。

消息也可以声明在另一个消息内部。

```proto
message Foo {
  message Bar {}
}
```

这会生成：

```objc
@interface Foo_Bar : GPBMessage
@end
```

可以看到，生成的嵌套消息名称由外围生成消息的名称（`Foo`）加上下划线（`_`）再加上嵌套消息名称（`Bar`）构成。

> **注意：** 我们已尽力确保把冲突降到最少，但由于下划线与驼峰命名之间的相互转换，消息名仍有可能发生冲突。例如：
>
> ```proto
> message foo_bar {}
> message foo { message bar {} }
> ```
>
> 两者都会生成 `@interface foo_bar` 并产生冲突。最务实的解决办法可能是重命名这些冲突的消息。

### `GPBMessage` 接口

`GPBMessage` 是所有生成消息类的超类。它必须支持以下接口的超集：

```objc
@interface GPBMessage : NSObject
@end
```

该接口的行为如下：

```objc
// 执行深拷贝。
- (id)copy;
// 执行深度相等比较。
- (BOOL)isEqual:(id)value;
```

### 未知字段

解析（parse）消息时，其中可能包含解析代码并不知道的字段。当消息是依据 .proto 定义的[旧版本（version）](/programming-guides/proto2#updating)创建、随后又用从较新版本生成的代码来解析时，就会出现这种情况（反之亦然）。

这些字段不会被丢弃，而是作为未知字段（unknown fields）存储在消息的 `unknownFields` 属性中：

```objc
@property(nonatomic, copy, nullable) GPBUnknownFieldSet *unknownFields;
```

你可以使用 `GPBUnknownFieldSet` 接口按编号获取这些字段，或者将它们当作数组进行遍历。

## 字段

以下各节描述 Protobuf 编译器为消息字段生成的代码。这些小节按隐式存在性（implicit presence）与显式存在性（explicit presence）划分。你可以在[字段存在性（field presence）](/programming-guides/field_presence)中进一步了解这一区别。

<a id="singular3"></a>

### 带隐式存在性的单数字段 {#singular-implicit}

对于每个单数字段（singular field），编译器会生成一个用于存储数据的属性，以及一个包含字段编号（field number）的整数常量。消息类型字段还会获得一个 `has..` 属性，让你可以检查该字段是否已在编码后的消息中设置。例如，给定以下消息：

```proto
message Foo {
  message Bar {
    int32 int32_value = 1;
  }
  enum Qux {...}
  int32 int32_value = 1;
  string string_value = 2;
  Bar message_value = 3;
  Qux enum_value = 4;
  bytes bytes_value = 5;
}
```

编译器将生成以下代码：

```objc
typedef GPB_ENUM(Foo_Bar_FieldNumber) {
  // 生成的字段编号名称是：外围消息名以下划线分隔，
  // 后接 "FieldNumber"，再接驼峰命名后的字段名。
  Foo_Bar_FieldNumber_Int32Value = 1,
};

@interface Foo_Bar : GPBMessage
@property(nonatomic, readwrite) int32_t int32Value;
@end

typedef GPB_ENUM(Foo_FieldNumber) {
  Foo_FieldNumber_Int32Value = 1,
  Foo_FieldNumber_StringValue = 2,
  Foo_FieldNumber_MessageValue = 3,
  Foo_FieldNumber_EnumValue = 4,
  Foo_FieldNumber_BytesValue = 5,
};

typedef GPB_ENUM(Foo_Qux) {
  Foo_Qux_GPBUnrecognizedEnumeratorValue = kGPBUnrecognizedEnumeratorValue,
  ...
};

@interface Foo : GPBMessage
// 字段名经过驼峰命名。
@property(nonatomic, readwrite) int32_t int32Value;
@property(nonatomic, readwrite, copy, null_resettable) NSString *stringValue;
@property(nonatomic, readwrite) BOOL hasMessageValue;
@property(nonatomic, readwrite, strong, null_resettable) Foo_Bar *messageValue;
@property(nonatomic, readwrite) Foo_Qux enumValue;
@property(nonatomic, readwrite, copy, null_resettable) NSData *bytesValue;
@end
```

#### 特殊命名情况

某些情况下，字段名生成规则可能造成名称冲突，此时需要对名称做“唯一化”（uniqued）处理。这类冲突的解决方式是在字段名末尾追加 `_p`（选用 `_p` 是因为它相当少见，且代表“property”，即属性）。

```proto
message Foo {
  int32 foo_array = 1;      // 以 Array 结尾
  int32 bar_OneOfCase = 2;  // 以 oneofcase 结尾
  int32 id = 3;             // 是 C/C++/Objective-C 关键字
}
```

生成：

```objc
typedef GPB_ENUM(Foo_FieldNumber) {
  // 如果非可重复字段的名称以 "Array" 结尾，则会加上 "_p"
  // 后缀，以与 repeated 类型区分。
  Foo_FieldNumber_FooArray_p = 1,
  // 如果字段名以 "OneOfCase" 结尾，则会加上 "_p" 后缀，
  // 以与 OneOfCase 属性区分。
  Foo_FieldNumber_BarOneOfCase_p = 2,
  // 如果字段名是 C/C++/ObjectiveC 关键字，则会加上 "_p" 后缀，
  // 以便能够编译。
  Foo_FieldNumber_Id_p = 3,
};

@interface Foo : GPBMessage
@property(nonatomic, readwrite) int32_t fooArray_p;
@property(nonatomic, readwrite) int32_t barOneOfCase_p;
@property(nonatomic, readwrite) int32_t id_p;
@end
```

#### 默认值 {#default}

数值类型的[默认值（default value）](/programming-guides/proto3#default)为 `0`。

字符串的默认值为 `@""`，bytes 的默认值为 `[NSData data]`。

向字符串字段赋 `nil` 在调试（debug）构建中会触发断言，在发布（release）构建中则会将字段设置为 `@""`。向 bytes 字段赋 `nil` 在调试构建中会触发断言，在发布构建中则会将字段设置为 `[NSData data]`。要判断某个 bytes 或字符串字段是否已设置，需要检测其 length 属性并与 0 比较。

消息的默认“空”值是默认消息的一个实例。要清除一个消息值，应将其设置为 `nil`。访问已清除的消息会返回默认消息的一个实例，并且 `hasFoo` 方法将返回 false。

为字段返回的默认消息是一个本地实例。返回默认消息而不是 `nil` 的原因在于，对于如下情形：

```proto
message Foo {
  message Bar {
     int32 b;
  }
  Bar a;
}
```

实现将支持以下写法：

```objc
Foo *foo = [[Foo alloc] init];
foo.a.b = 2;
```

其中 `a` 会在必要时通过访问器自动创建。如果 `foo.a` 返回 `nil`，`foo.a.b` 这种赋值写法就无法工作。

<a id="singular2"></a>

### 带显式存在性的单数字段 {#singular-explicit}

对于每个单数字段，编译器会生成一个用于存储数据的属性、一个包含字段编号的整数常量，以及一个 `has..` 属性（让你可以检查该字段是否已在编码后的消息中设置）。例如，给定以下消息：

```proto
message Foo {
  message Bar {
    int32 int32_value = 1;
  }
  enum Qux {...}
  optional int32 int32_value = 1;
  optional string string_value = 2;
  optional Bar message_value = 3;
  optional Qux enum_value = 4;
  optional bytes bytes_value = 5;
}
```

编译器将生成以下代码：

```objc
# 枚举 Foo_Qux

typedef GPB_ENUM(Foo_Qux) {
  Foo_Qux_Flupple = 0,
};

GPBEnumDescriptor *Foo_Qux_EnumDescriptor(void);

BOOL Foo_Qux_IsValidValue(int32_t value);

# 消息 Foo

typedef GPB_ENUM(Foo_FieldNumber) {
  Foo_FieldNumber_Int32Value = 2,
  Foo_FieldNumber_MessageValue = 3,
  Foo_FieldNumber_EnumValue = 4,
  Foo_FieldNumber_BytesValue = 5,
  Foo_FieldNumber_StringValue = 6,
};

@interface Foo : GPBMessage

@property(nonatomic, readwrite) BOOL hasInt32Value;
@property(nonatomic, readwrite) int32_t int32Value;

@property(nonatomic, readwrite) BOOL hasStringValue;
@property(nonatomic, readwrite, copy, null_resettable) NSString *stringValue;

@property(nonatomic, readwrite) BOOL hasMessageValue;
@property(nonatomic, readwrite, strong, null_resettable) Foo_Bar *messageValue;

@property(nonatomic, readwrite) BOOL hasEnumValue;
@property(nonatomic, readwrite) Foo_Qux enumValue;

@property(nonatomic, readwrite) BOOL hasBytesValue;
@property(nonatomic, readwrite, copy, null_resettable) NSData *bytesValue;

@end

# 消息 Foo_Bar

typedef GPB_ENUM(Foo_Bar_FieldNumber) {
  Foo_Bar_FieldNumber_Int32Value = 1,
};

@interface Foo_Bar : GPBMessage

@property(nonatomic, readwrite) BOOL hasInt32Value;
@property(nonatomic, readwrite) int32_t int32Value;

@end
```

#### 特殊命名情况

某些情况下，字段名生成规则可能造成名称冲突，此时需要对名称做“唯一化”（uniqued）处理。这类冲突的解决方式是在字段名末尾追加 `_p`（选用 `_p` 是因为它相当少见，且代表“property”，即属性）。

```proto
message Foo {
  optional int32 foo_array = 1;      // 以 Array 结尾
  optional int32 bar_OneOfCase = 2;  // 以 oneofcase 结尾
  optional int32 id = 3;             // 是 C/C++/Objective-C 关键字
}
```

生成：

```objc
typedef GPB_ENUM(Foo_FieldNumber) {
  // 如果非可重复字段的名称以 "Array" 结尾，则会加上 "_p"
  // 后缀，以与 repeated 类型区分。
  Foo_FieldNumber_FooArray_p = 1,
  // 如果字段名以 "OneOfCase" 结尾，则会加上 "_p" 后缀，
  // 以与 OneOfCase 属性区分。
  Foo_FieldNumber_BarOneOfCase_p = 2,
  // 如果字段名是 C/C++/ObjectiveC 关键字，则会加上 "_p" 后缀，
  // 以便能够编译。
  Foo_FieldNumber_Id_p = 3,
};

@interface Foo : GPBMessage
@property(nonatomic, readwrite) int32_t fooArray_p;
@property(nonatomic, readwrite) int32_t barOneOfCase_p;
@property(nonatomic, readwrite) int32_t id_p;
@end
```

#### 默认值（仅限 optional 字段）{#default}

在用户未显式指定默认值的情况下，数值类型的[默认值](/programming-guides/proto2#optional)为 `0`。

字符串的默认值为 `@""`，bytes 的默认值为 `[NSData data]`。

向字符串字段赋 `nil` 在调试构建中会触发断言，在发布构建中则会将字段设置为 `@""`。向 bytes 字段赋 `nil` 在调试构建中会触发断言，在发布构建中则会将字段设置为 `[NSData data]`。要判断某个 bytes 或字符串字段是否已设置，需要检测其 length 属性并与 0 比较。

消息的默认“空”值是默认消息的一个实例。要清除一个消息值，应将其设置为 `nil`。访问已清除的消息会返回默认消息的一个实例，并且 `hasFoo` 方法将返回 false。

为字段返回的默认消息是一个本地实例。返回默认消息而不是 `nil` 的原因在于，对于如下情形：

```proto
message Foo {
  message Bar {
     int32 b;
  }
  Bar a;
}
```

实现将支持以下写法：

```objc
Foo *foo = [[Foo alloc] init];
foo.a.b = 2;
```

其中 `a` 会在必要时通过访问器自动创建。如果 `foo.a` 返回 `nil`，`foo.a.b` 这种赋值写法就无法工作。

### repeated 字段 {#repeated}

与单数字段（[proto2](#singular2) [proto3](#singular3)）一样，Protobuf 编译器会为每个 repeated 字段生成一个数据属性。该数据属性根据字段类型是一个 `GPB<VALUE>Array`，其中 `<VALUE>` 可以是 `UInt32`、`Int32`、`UInt64`、`Int64`、`Bool`、`Float`、`Double` 或 `Enum`。对于 `string`、`bytes` 和 `message` 类型，则会使用 `NSMutableArray`。repeated 类型的字段名末尾会附加 `Array`。在 Objective-C 接口中附加 `Array` 的目的是让代码更易读。proto 文件中的 repeated 字段往往使用单数名称，这在标准 Objective-C 用法中读起来并不通顺。把单数名称变成复数会更符合 Objective-C 的习惯，但复数化规则过于复杂，编译器无法支持。

```proto
message Foo {
  message Bar {}
  enum Qux {}
  repeated int32 int32_value = 1;
  repeated string string_value = 2;
  repeated Bar message_value = 3;
  repeated Qux enum_value = 4;
}
```

生成：

```objc
typedef GPB_ENUM(Foo_FieldNumber) {
  Foo_FieldNumber_Int32ValueArray = 1,
  Foo_FieldNumber_StringValueArray = 2,
  Foo_FieldNumber_MessageValueArray = 3,
  Foo_FieldNumber_EnumValueArray = 4,
};

@interface Foo : GPBMessage
// repeated 类型的字段名是驼峰命名名称加上 "Array" 后缀。
@property(nonatomic, readwrite, strong, null_resettable)
 GPBInt32Array *int32ValueArray;
@property(nonatomic, readonly) NSUInteger int32ValueArray_Count;

@property(nonatomic, readwrite, strong, null_resettable)
 NSMutableArray *stringValueArray;
@property(nonatomic, readonly) NSUInteger stringValueArray_Count;

@property(nonatomic, readwrite, strong, null_resettable)
 NSMutableArray *messageValueArray;
@property(nonatomic, readonly) NSUInteger messageValueArray_Count;

@property(nonatomic, readwrite, strong, null_resettable)
 GPBEnumArray *enumValueArray;
@property(nonatomic, readonly) NSUInteger enumValueArray_Count;
@end
```

**注意：** 在版次中，repeated 字段的行为可以通过 [`features.repeated_field_encoding` 特性（feature）](/editions/features#repeated_field_encoding)进行配置。

对于 string、bytes 和 message 字段，数组元素分别是 `NSString*`、`NSData*` 和指向 `GPBMessage` 子类的指针。

#### 默认值 {#repeateddefault}

repeated 字段的[默认值](/programming-guides/proto3#default)为空。在 Objective-C 生成代码中，这是一个空的 `GPB<VALUE>Array`。如果你访问一个空的 repeated 字段，会得到一个空数组，你可以像更新任何其他 repeated 字段数组一样更新它。

```objc
Foo *myFoo = [[Foo alloc] init];
[myFoo.stringValueArray addObject:@"A string"]
```

你也可以使用提供的 `<field>Array_Count` 属性来检查某个特定 repeated 字段的数组是否为空，而无需创建该数组：

```objc
if (myFoo.messageValueArray_Count) {
  // 数组中有内容……
}
```

#### `GPB<VALUE>Array` 接口

`GPB<VALUE>Array`（下文将介绍的 `GPBEnumArray` 除外）具有如下接口：

```objc
@interface GPBArray : NSObject
@property (nonatomic, readonly) NSUInteger count;
+ (instancetype)array;
+ (instancetype)arrayWithValue:()value;
+ (instancetype)arrayWithValueArray:(GPBArray *)array;
+ (instancetype)arrayWithCapacity:(NSUInteger)count;

// 初始化数组，复制其中的值。
- (instancetype)initWithValueArray:(GPBArray *)array;
- (instancetype)initWithValues:(const  [])values
                         count:(NSUInteger)count NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithCapacity:(NSUInteger)count;

- ()valueAtIndex:(NSUInteger)index;

- (void)enumerateValuesWithBlock:
     (void (^)( value, NSUInteger idx, BOOL *stop))block;
- (void)enumerateValuesWithOptions:(NSEnumerationOptions)opts
    usingBlock:(void (^)( value, NSUInteger idx, BOOL *stop))block;

- (void)addValue:()value;
- (void)addValues:(const  [])values count:(NSUInteger)count;
- (void)addValuesFromArray:(GPBArray *)array;

- (void)removeValueAtIndex:(NSUInteger)count;
- (void)removeAll;

- (void)exchangeValueAtIndex:(NSUInteger)idx1
            withValueAtIndex:(NSUInteger)idx2;
- (void)insertValue:()value atIndex:(NSUInteger)count;
- (void)replaceValueAtIndex:(NSUInteger)index withValue:()value;


@end
```

`GPBEnumArray` 的接口略有不同，用于处理校验函数（validation function）并访问原始值（raw value）。

```objc
@interface GPBEnumArray : NSObject
@property (nonatomic, readonly) NSUInteger count;
@property (nonatomic, readonly) GPBEnumValidationFunc validationFunc;

+ (instancetype)array;
+ (instancetype)arrayWithValidationFunction:(nullable GPBEnumValidationFunc)func;
+ (instancetype)arrayWithValidationFunction:(nullable GPBEnumValidationFunc)func
                                   rawValue:value;
+ (instancetype)arrayWithValueArray:(GPBEnumArray *)array;
+ (instancetype)arrayWithValidationFunction:(nullable GPBEnumValidationFunc)func
                                   capacity:(NSUInteger)count;

- (instancetype)initWithValidationFunction:
  (nullable GPBEnumValidationFunc)func;

// 初始化数组，复制其中的值。
- (instancetype)initWithValueArray:(GPBEnumArray *)array;
- (instancetype)initWithValidationFunction:(nullable GPBEnumValidationFunc)func
    values:(const int32_t [])values
    count:(NSUInteger)count NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithValidationFunction:(nullable GPBEnumValidationFunc)func
                                  capacity:(NSUInteger)count;

// 如果索引处的值不是 validationFunc 所定义的有效枚举项（enumerator），
// 这些方法将返回 kGPBUnrecognizedEnumeratorValue。如果需要实际的值，
// 请使用该方法的 "raw" 版本。
- (int32_t)valueAtIndex:(NSUInteger)index;
- (void)enumerateValuesWithBlock:
    (void (^)(int32_t value, NSUInteger idx, BOOL *stop))block;
- (void)enumerateValuesWithOptions:(NSEnumerationOptions)opts
    usingBlock:(void (^)(int32_t value, NSUInteger idx, BOOL *stop))block;

// 这些方法绕过 validationFunc，用于访问二进制文件编译时
// 尚未知的值。
- (int32_t)rawValueAtIndex:(NSUInteger)index;

- (void)enumerateRawValuesWithBlock:
    (void (^)(int32_t value, NSUInteger idx, BOOL *stop))block;
- (void)enumerateRawValuesWithOptions:(NSEnumerationOptions)opts
    usingBlock:(void (^)(int32_t value, NSUInteger idx, BOOL *stop))block;

// 如果值不是 validationFunc 所定义的有效枚举项，这些方法会在调试构建中
// 触发断言，在发布构建中记录日志并将该值设为默认值。
// 若要赋非枚举项的值，请使用下方的 rawValue 方法。
- (void)addValue:(int32_t)value;
- (void)addValues:(const int32_t [])values count:(NSUInteger)count;
- (void)insertValue:(int32_t)value atIndex:(NSUInteger)count;
- (void)replaceValueAtIndex:(NSUInteger)index withValue:(int32_t)value;

// 这些方法绕过 validationFunc，用于设置二进制文件编译时
// 尚未知的值。
- (void)addRawValue:(int32_t)rawValue;
- (void)addRawValuesFromEnumArray:(GPBEnumArray *)array;
- (void)addRawValues:(const int32_t [])values count:(NSUInteger)count;
- (void)replaceValueAtIndex:(NSUInteger)index withRawValue:(int32_t)rawValue;
- (void)insertRawValue:(int32_t)value atIndex:(NSUInteger)count;

// 这些方法不进行任何校验。
- (void)removeValueAtIndex:(NSUInteger)count;
- (void)removeAll;
- (void)exchangeValueAtIndex:(NSUInteger)idx1
            withValueAtIndex:(NSUInteger)idx2;

@end
```

### oneof 字段 {#oneof}

给定包含 [oneof](/programming-guides/proto3#oneof) 字段定义的消息：

```proto
message Order {
  oneof OrderID {
    string name = 1;
    int32 address = 2;
  };
  int32 quantity = 3;
};
```

Protobuf 编译器会生成：

```objc
typedef GPB_ENUM(Order_OrderID_OneOfCase) {
  Order_OrderID_OneOfCase_GPBUnsetOneOfCase = 0,
  Order_OrderID_OneOfCase_Name = 1,
  Order_OrderID_OneOfCase_Address = 2,
};

typedef GPB_ENUM(Order_FieldNumber) {
  Order_FieldNumber_Name = 1,
  Order_FieldNumber_Address = 2,
  Order_FieldNumber_Quantity = 3,
};

@interface Order : GPBMessage
@property (nonatomic, readwrite) Order_OrderID_OneOfCase orderIDOneOfCase;
@property (nonatomic, readwrite, copy, null_resettable) NSString *name;
@property (nonatomic, readwrite) int32_t address;
@property (nonatomic, readwrite) int32_t quantity;
@end

void Order_ClearOrderIDOneOfCase(Order *message);
```

设置 oneof 的某个属性会清除与该 oneof 关联的所有其他属性。

`<ONE_OF_NAME>_OneOfCase_GPBUnsetOneOfCase` 始终等价于 0，便于轻松测试 oneof 中是否有任何字段已被设置。

### map 字段

对于以下消息定义：

```proto
message Bar {...}
message Foo {
  map<int32, string> a_map = 1;
  map<string, Bar> b_map = 2;
};
```

编译器会生成以下代码：

```objc
typedef GPB_ENUM(Foo_FieldNumber) {
  Foo_FieldNumber_AMap = 1,
  Foo_FieldNumber_BMap = 2,
};

@interface Foo : GPBMessage
// map 名称是字段名的驼峰命名版本。
@property (nonatomic, readwrite, strong, null_resettable) GPBInt32ObjectDictionary *aMap;
@property(nonatomic, readonly) NSUInteger aMap_Count;
@property (nonatomic, readwrite, strong, null_resettable) NSMutableDictionary *bMap;
@property(nonatomic, readonly) NSUInteger bMap_Count;
@end
```

键为字符串、且值为字符串、bytes 或消息的情况由 `NSMutableDictionary` 处理。

其他情况则是：

```objc
GBP<KEY><VALUE>Dictionary
```

其中：

-   `<KEY>` 为 Uint32、Int32、UInt64、Int64、Bool 或 String。
-   `<VALUE>` 为 UInt32、Int32、UInt64、Int64、Bool、Float、Double、Enum 或 Object。`Object` 用于 `string`、`bytes` 或 `message` 类型的值，以减少类的数量，并与 Objective-C 处理 `NSMutableDictionary` 的方式保持一致。

#### 默认值 {#repeateddefault}

map 字段的[默认值](/programming-guides/proto3#default)为空。在 Objective-C 生成代码中，这是一个空的 `GBP<KEY><VALUE>Dictionary`。如果你访问一个空的 map 字段，会得到一个空字典，你可以像更新任何其他 map 字段一样更新它。

你也可以使用提供的 `<mapField>_Count` 属性来检查某个特定 map 是否为空：

```objc
if (myFoo.myMap_Count) {
  // map 中有内容……
}
```

#### `GBP<KEY><VALUE>Dictionary` 接口

`GBP<KEY><VALUE>Dictionary`（`GBP<KEY>ObjectDictionary` 和 `GBP<KEY>EnumDictionary` 除外）的接口如下：

```objc
@interface GPB<KEY>Dictionary : NSObject
@property (nonatomic, readonly) NSUInteger count;

+ (instancetype)dictionary;
+ (instancetype)dictionaryWithValue:(const )value
                             forKey:(const <KEY>)key;
+ (instancetype)dictionaryWithValues:(const  [])values
                             forKeys:(const <KEY> [])keys
                               count:(NSUInteger)count;
+ (instancetype)dictionaryWithDictionary:(GPB<KEY>Dictionary *)dictionary;
+ (instancetype)dictionaryWithCapacity:(NSUInteger)numItems;

- (instancetype)initWithValues:(const  [])values
                       forKeys:(const <KEY> [])keys
                         count:(NSUInteger)count NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithDictionary:(GPB<KEY>Dictionary *)dictionary;
- (instancetype)initWithCapacity:(NSUInteger)numItems;

- (BOOL)valueForKey:(<KEY>)key value:(VALUE *)value;

- (void)enumerateKeysAndValuesUsingBlock:
    (void (^)(<KEY> key,  value, BOOL *stop))block;

- (void)removeValueForKey:(<KEY>)aKey;
- (void)removeAll;
- (void)setValue:()value forKey:(<KEY>)key;
- (void)addEntriesFromDictionary:(GPB<KEY>Dictionary *)otherDictionary;
@end
```

`GBP<KEY>ObjectDictionary` 的接口为：

```objc
@interface GPB<KEY>ObjectDictionary : NSObject
@property (nonatomic, readonly) NSUInteger count;

+ (instancetype)dictionary;
+ (instancetype)dictionaryWithObject:(id)object
                             forKey:(const <KEY>)key;
+ (instancetype)
  dictionaryWithObjects:(const id GPB_UNSAFE_UNRETAINED [])objects
                forKeys:(const <KEY> [])keys
                  count:(NSUInteger)count;
+ (instancetype)dictionaryWithDictionary:(GPB<KEY>ObjectDictionary *)dictionary;
+ (instancetype)dictionaryWithCapacity:(NSUInteger)numItems;

- (instancetype)initWithObjects:(const id GPB_UNSAFE_UNRETAINED [])objects
                        forKeys:(const <KEY> [])keys
                          count:(NSUInteger)count NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithDictionary:(GPB<KEY>ObjectDictionary *)dictionary;
- (instancetype)initWithCapacity:(NSUInteger)numItems;

- (id)objectForKey:(uint32_t)key;

- (void)enumerateKeysAndObjectsUsingBlock:
    (void (^)(<KEY> key, id object, BOOL *stop))block;

- (void)removeObjectForKey:(<KEY>)aKey;
- (void)removeAll;
- (void)setObject:(id)object forKey:(<KEY>)key;
- (void)addEntriesFromDictionary:(GPB<KEY>ObjectDictionary *)otherDictionary;
@end
```

`GBP<KEY>EnumDictionary` 的接口略有不同，用于处理校验函数并访问原始值。

```objc
@interface GPB<KEY>EnumDictionary : NSObject

@property(nonatomic, readonly) NSUInteger count;
@property(nonatomic, readonly) GPBEnumValidationFunc validationFunc;

+ (instancetype)dictionary;
+ (instancetype)dictionaryWithValidationFunction:(nullable GPBEnumValidationFunc)func;
+ (instancetype)dictionaryWithValidationFunction:(nullable GPBEnumValidationFunc)func
                                        rawValue:(int32_t)rawValue
                                          forKey:(<KEY>_t)key;
+ (instancetype)dictionaryWithValidationFunction:(nullable GPBEnumValidationFunc)func
                                       rawValues:(const int32_t [])values
                                         forKeys:(const <KEY>_t [])keys
                                           count:(NSUInteger)count;
+ (instancetype)dictionaryWithDictionary:(GPB<KEY>EnumDictionary *)dictionary;
+ (instancetype)dictionaryWithValidationFunction:(nullable GPBEnumValidationFunc)func
                                        capacity:(NSUInteger)numItems;

- (instancetype)initWithValidationFunction:(nullable GPBEnumValidationFunc)func;
- (instancetype)initWithValidationFunction:(nullable GPBEnumValidationFunc)func
                                 rawValues:(const int32_t [])values
                                   forKeys:(const <KEY>_t [])keys
                                     count:(NSUInteger)count NS_DESIGNATED_INITIALIZER;
- (instancetype)initWithDictionary:(GPB<KEY>EnumDictionary *)dictionary;
- (instancetype)initWithValidationFunction:(nullable GPBEnumValidationFunc)func
                                  capacity:(NSUInteger)numItems;

// 如果键对应的值不是 validationFunc 所定义的有效枚举项，
// 这些方法将返回 kGPBUnrecognizedEnumeratorValue。如果需要实际的值，
// 请使用该方法的 "raw" 版本。

- (BOOL)valueForKey:(<KEY>_t)key value:(nullable int32_t *)value;

- (void)enumerateKeysAndValuesUsingBlock:
    (void (^)(<KEY>_t key, int32_t value, BOOL *stop))block;

// 这些方法绕过 validationFunc，用于访问二进制文件编译时
// 尚未知的值。

- (BOOL)valueForKey:(<KEY>_t)key rawValue:(nullable int32_t *)rawValue;

- (void)enumerateKeysAndRawValuesUsingBlock:
    (void (^)(<KEY>_t key, int32_t rawValue, BOOL *stop))block;

- (void)addRawEntriesFromDictionary:(GPB<KEY>EnumDictionary *)otherDictionary;

// 如果值不是 validationFunc 所定义的有效枚举项，这些方法会在调试构建中
// 触发断言，在发布构建中记录日志并将该值设为默认值。
// 若要赋非枚举项的值，请使用下方的 rawValue 方法。

- (void)setValue:(int32_t)value forKey:(<KEY>_t)key;

// 此方法绕过 validationFunc，用于设置二进制文件编译时
// 尚未知的值。
- (void)setRawValue:(int32_t)rawValue forKey:(<KEY>_t)key;

// 这些方法不进行任何校验。

- (void)removeValueForKey:(<KEY>_t)aKey;
- (void)removeAll;

@end
```

## 枚举 {#enum}

给定如下枚举定义：

```proto
enum Foo {
  VALUE_A = 0;
  VALUE_B = 1;
  VALUE_C = 5;
}
```

生成的代码将是：

```objc
// 生成的枚举值名称是：枚举名加上下划线，
// 再加上转换为驼峰命名的枚举项名。
// GPB_ENUM 是 Objective-C Protobuf 头文件中定义的宏，
// 它强制所有枚举值均为 int32，并有助于支持 Swift 枚举。
typedef GPB_ENUM(Foo) {
  Foo_GPBUnrecognizedEnumeratorValue = kGPBUnrecognizedEnumeratorValue, //仅限 proto3
  Foo_ValueA = 0,
  Foo_ValueB = 1;
  Foo_ValueC = 5;
};

// 返回有关此枚举类型定义了哪些值的信息。
GPBEnumDescriptor *Foo_EnumDescriptor();
```

每个枚举都会为其声明一个校验函数：

```objc
// 如果给定的数值与 Foo 定义的某个值（0、1、5）匹配，则返回 YES。
BOOL Foo_IsValidValue(int32_t value);
```

以及一个为其声明的枚举描述符（descriptor）访问器函数：

```objc
// GPBEnumDescriptor 定义在运行时中，包含有关枚举定义的信息，
// 例如枚举名、枚举值和枚举值校验函数。
typedef GPBEnumDescriptor *(*GPBEnumDescriptorAccessorFunc)();
```

枚举描述符访问器函数是 C 函数，而不是枚举类上的方法，因为客户端软件很少使用它们。这可以减少生成的 Objective-C 运行时（runtime）信息量，并可能让链接器将其作为死代码剔除。

对于名称与任何 C/C++ 或 Objective-C 关键字相同的外层枚举，例如：

```proto
enum method {}
```

生成的接口会加上 `_Enum` 后缀，如下所示：

```objc
// 生成的枚举名是关键字加上 _Enum 后缀。
typedef GPB_ENUM(Method_Enum) {}
```

枚举也可以声明在另一个消息内部。例如：

```proto
message Foo {
  enum Bar {
    VALUE_A = 0;
    VALUE_B = 1;
    VALUE_C = 5;
  }
  Bar aBar = 1;
  Bar aDifferentBar = 2;
  repeated Bar aRepeatedBar = 3;
}
```

生成：

```objc
typedef GPB_ENUM(Foo_Bar) {
  Foo_Bar_GPBUnrecognizedEnumeratorValue = kGPBUnrecognizedEnumeratorValue, //仅限 proto3
  Foo_Bar_ValueA = 0;
  Foo_Bar_ValueB = 1;
  Foo_Bar_ValueC = 5;
};

GPBEnumDescriptor *Foo_Bar_EnumDescriptor();

BOOL Foo_Bar_IsValidValue(int32_t value);

@interface Foo : GPBMessage
@property (nonatomic, readwrite) Foo_Bar aBar;
@property (nonatomic, readwrite) Foo_Bar aDifferentBar;
@property (nonatomic, readwrite, strong, null_resettable)
 GPBEnumArray *aRepeatedBarArray;
@end

// 仅限 proto3：每个包含枚举字段的消息都会有一个访问器函数，
// 用于以整数形式获取该枚举的值。这使客户端可以在需要时处理原始值。
int32_t Foo_ABar_RawValue(Foo *message);
void SetFoo_ABar_RawValue(Foo *message, int32_t value);
int32_t Foo_ADifferentBar_RawValue(Foo *message);
void SetFoo_ADifferentBar_RawValue(Foo *message, int32_t value);
```

所有枚举字段都可以将值作为有类型的枚举项（enumerator）访问（即上例中的 `Foo_Bar`），或者在使用 proto3 时作为原始的 `int32_t` 值访问（使用上例中的访问器函数）。这是为了支持这样一种情况：由于客户端和服务器使用不同版本的 proto 文件编译，服务器返回的值客户端可能无法识别。

无法识别的枚举值的处理方式取决于语言版本以及版次中的 `features.enum_type` 特性。

*   在开放式枚举（open enum）中，如果解析出的消息数据中的枚举项值不是读取它的代码在编译时所支持的值，则有类型的枚举项值将返回 `kGPBUnrecognizedEnumeratorValue`。如果需要实际的值，请使用原始值访问器以 `int32_t` 形式获取该值。
*   在封闭式枚举（closed enum）中，无法识别的枚举值会被当作未知字段处理。
*   proto2 的枚举是封闭式的，proto3 的枚举是开放式的。在版次中，该行为可通过 `features.enum_type` 特性配置。

`kGPBUnrecognizedEnumeratorValue` 被定义为 `0xFBADBEEF`，如果枚举中的任何枚举项具有此值，将是一个错误。尝试将任何枚举字段设置为该值是一个运行时错误。类似地，尝试使用有类型的访问器将任何枚举字段设置为其枚举类型未定义的枚举项，也是一个运行时错误。在这两种错误情况下，调试构建会触发断言，发布构建会记录日志并将该字段设置为其默认值（`0`）。

原始值访问器被定义为 C 函数而不是 Objective-C 方法，因为在大多数情况下不会用到它们。将它们声明为 C 函数可以减少浪费的 Objective-C 运行时信息，并可能让链接器将其作为死代码剔除。

### Swift 枚举支持

Apple 在[《与 C API 交互》（Interacting with C APIs）](https://developer.apple.com/library/ios/documentation/Swift/Conceptual/BuildingCocoaApps/InteractingWithCAPIs.html#//apple_ref/doc/uid/TP40014216-CH8-XID_11)中说明了如何将 Objective-C 枚举导入为 Swift 枚举。Protobuf 生成的枚举支持 Objective-C 到 Swift 的转换。

```proto
// Proto
enum Foo {
  VALUE_A = 0;
}
```

生成：

```objc
// Objective-C
typedef GPB_ENUM(Foo) {
  Foo_GPBUnrecognizedEnumeratorValue = kGPBUnrecognizedEnumeratorValue,
  Foo_ValueA = 0,
};
```

在 Swift 代码中则可以这样使用：

```swift
// Swift
let aValue = Foo.ValueA
let anotherValue: Foo = .GPBUnrecognizedEnumeratorValue
```

## 知名类型 {#wellknown}

如果你使用 Protobuf 提供的任何消息类型，它们在生成的 Objective-C 代码中通常就直接沿用其 proto 定义；不过我们通过分类（category）提供了一些基本的转换方法，以便更简单地使用它们。注意，我们尚未为所有知名类型（well-known types）提供专用 API，其中包括 [`Any`](/programming-guides/proto3#any)（目前尚无辅助方法可将 `Any` 的消息值转换为相应类型的消息）。

### 时间戳

```objc
@interface GPBTimeStamp (GPBWellKnownTypes)
@property (nonatomic, readwrite, strong) NSDate *date;
@property (nonatomic, readwrite) NSTimeInterval timeIntervalSince1970;
- (instancetype)initWithDate:(NSDate *)date;
- (instancetype)initWithTimeIntervalSince1970:
    (NSTimeInterval)timeIntervalSince1970;
@end
```

### Duration

```objc
@interface GPBDuration (GPBWellKnownTypes)
@property (nonatomic, readwrite) NSTimeInterval timeIntervalSince1970;
- (instancetype)initWithTimeIntervalSince1970:
    (NSTimeInterval)timeIntervalSince1970;
@end
```

## 扩展（仅限 proto2 和版次）{#extensions}

你可以使用 `extension_generation_mode` 选项来控制扩展的生成方式。共有三种模式：

*   `class_based`：为扩展生成 Objective-C 类和方法（旧版）。
*   `c_function`：为扩展生成 C 函数（新版）。
*   `migration`：两者都生成。

### 基于类（旧版）{#extensions-legacy}

给定一个带有[扩展区间（extension range）](/programming-guides/proto2#extensions)的消息：

```proto
message Foo {
  extensions 100 to 199;
}

extend Foo {
  int32 foo = 101;
  repeated int32 repeated_foo = 102;
}

message Bar {
  extend Foo {
    int32 bar = 103;
    repeated int32 repeated_bar = 104;
  }
}
```

编译器会生成以下代码：

```objc
# 文件 Test2Root

@interface Test2Root : GPBRootObject

// 基类提供了：
//   + (GPBExtensionRegistry *)extensionRegistry;
// 方法，它是一个 GPBExtensionRegistry，包含本文件及其依赖的
// 所有文件所定义的全部扩展。

@end

@interface Test2Root (DynamicMethods)
+ (GPBExtensionDescriptor *)foo;
+ (GPBExtensionDescriptor *)repeatedFoo;
@end

# 消息 Foo

@interface Foo : GPBMessage

@end

# 消息 Bar

@interface Bar : GPBMessage

@end

@interface Bar (DynamicMethods)

+ (GPBExtensionDescriptor *)bar;
+ (GPBExtensionDescriptor *)repeatedBar;
@end
```

要获取和设置这些扩展字段，可以使用以下代码：

```objc
Foo *fooMsg = [[Foo alloc] init];

// 设置单数字段的扩展
[fooMsg setExtension:[Test2Root foo] value:@5];
NSAssert([fooMsg hasExtension:[Test2Root foo]]);
NSAssert([[fooMsg getExtension:[Test2Root foo]] intValue] == 5);

// 向 repeated 扩展添加两项：
[fooMsg addExtension:[Test2Root repeatedFoo] value:@1];
[fooMsg addExtension:[Test2Root repeatedFoo] value:@2];
NSAssert([fooMsg hasExtension:[Test2Root repeatedFoo]]);
NSAssert([[fooMsg getExtension:[Test2Root repeatedFoo]] count] == 2);

// 清除
[fooMsg clearExtension:[Test2Root foo]];
[fooMsg clearExtension:[Test2Root repeatedFoo]];
NSAssert(![fooMsg hasExtension:[Test2Root foo]]);
NSAssert(![fooMsg hasExtension:[Test2Root repeatedFoo]]);
```

### C 函数（新版）{#extensions-c-functions}

使用 `c_function` 模式时，会生成 C 函数而不是 Objective-C 类。这可以减小二进制体积并避免名称冲突。

生成函数的命名约定涉及 proto 包名和扩展名。如果定义了 `objc_class_prefix`，会将其前置。

*   文件级注册表：`<Prefix><Package>_<File>_Registry()`
*   文件级扩展：`<Prefix><Package>_extension_<Field>()`
*   消息级扩展：
    `<Prefix><Package>_<ScopeMessage>_extension_<Field>()`

（注意：`Package` 是驼峰命名后的 proto 包名。`File` 是文件名。`ScopeMessage` 是包含扩展定义的消息。）

使用与上面相同的示例，但假定 `package my.package;` 且文件为 `test2.proto`：

编译器会生成在头文件中声明的 C 函数：

```objc
// 该文件的注册表函数。
GPBExtensionRegistry *MyPackage_Test2_Registry(void);

// 文件级扩展。
GPBExtensionDescriptor *MyPackage_extension_Foo(void);
GPBExtensionDescriptor *MyPackage_extension_RepeatedFoo(void);

// 消息级扩展（作用域为 Bar）。
GPBExtensionDescriptor *MyPackage_Bar_extension_Bar(void);
GPBExtensionDescriptor *MyPackage_Bar_extension_RepeatedBar(void);
```

要获取和设置这些扩展字段：

```objc
Foo *fooMsg = [[Foo alloc] init];

// 设置单数字段的扩展
[fooMsg setExtension:MyPackage_extension_Foo() value:@5];
NSAssert([fooMsg hasExtension:MyPackage_extension_Foo()]);
NSAssert([[fooMsg getExtension:MyPackage_extension_Foo()] intValue] == 5);

// 向 repeated 扩展添加两项：
[fooMsg addExtension:MyPackage_extension_RepeatedFoo() value:@1];
[fooMsg addExtension:MyPackage_extension_RepeatedFoo() value:@2];
NSAssert([fooMsg hasExtension:MyPackage_extension_RepeatedFoo()]);
NSAssert([[fooMsg getExtension:MyPackage_extension_RepeatedFoo()] count] == 2);

// 清除
[fooMsg clearExtension:MyPackage_extension_Foo()];
[fooMsg clearExtension:MyPackage_extension_RepeatedFoo()];
NSAssert(![fooMsg hasExtension:MyPackage_extension_Foo()]);
NSAssert(![fooMsg hasExtension:MyPackage_extension_RepeatedFoo()]);
```
