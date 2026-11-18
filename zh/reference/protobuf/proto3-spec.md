+++
title = "Protobuf proto3 语言规范"
weight = 810
linkTitle = "proto3 语言规范"
description = "Protobuf 语言 proto3 的语言规范参考。"
type = "docs"
source_url = "https://protobuf.dev/reference/protobuf/proto3-spec/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

**说明：**已知本语言规范尚不完整，尤其是在空白处理和其他词法细节方面。C++ `protoc` 编译器的实现才是权威的事实来源。本文档尽力描述这一手写解析器的行为，该解析器并非基于形式文法。

语法采用[扩展巴科斯-瑙尔范式（EBNF）](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_Form)描述：

```
|   选择
()  分组
[]  可选（出现零次或一次）
{}  重复（出现任意次数）
```

有关 proto3 用法的更多信息，请参阅[语言指南](/programming-guides/proto3)。

## 词法元素 {#lexical_elements}

### 字母与数字 {#letters_and_digits}

```
letter = "A" ... "Z" | "a" ... "z"
decimalDigit = "0" ... "9"
octalDigit   = "0" ... "7"
hexDigit     = "0" ... "9" | "A" ... "F" | "a" ... "f"
```

### 标识符

```
ident = letter { letter | decimalDigit | "_" }
fullIdent = ident { "." ident }
messageName = ident
enumName = ident
fieldName = ident
oneofName = ident
mapName = ident
serviceName = ident
rpcName = ident
messageType = [ "." ] { ident "." } messageName
enumType = [ "." ] { ident "." } enumName
```

### 整数字面量 {#integer_literals}

```
intLit     = decimalLit | octalLit | hexLit
decimalLit = [-] ( "1" ... "9" ) { decimalDigit }
octalLit   = [-] "0" { octalDigit }
hexLit     = [-] "0" ( "x" | "X" ) hexDigit { hexDigit }
```

### 浮点数字面量

```
floatLit = [-] ( decimals "." [ decimals ] [ exponent ] | decimals exponent | "."decimals [ exponent ] ) | "inf" | "nan"
decimals  = [-] decimalDigit { decimalDigit }
exponent  = ( "e" | "E" ) [ "+" | "-" ] decimals
```

### 布尔值

```
boolLit = "true" | "false"
```

### 字符串字面量 {#string_literals}

```
strLit = strLitSingle { strLitSingle }
strLitSingle = ( "'" { charValue } "'" ) |  ( '"' { charValue } '"' )
charValue = hexEscape | octEscape | charEscape | unicodeEscape | unicodeLongEscape | /[^\0\n\\]/
hexEscape = '\' ( "x" | "X" ) hexDigit [ hexDigit ]
octEscape = '\' octalDigit [ octalDigit [ octalDigit ] ]
charEscape = '\' ( "a" | "b" | "f" | "n" | "r" | "t" | "v" | '\' | "'" | '"' )
unicodeEscape = '\' "u" hexDigit hexDigit hexDigit hexDigit
unicodeLongEscape = '\' "U" ( "000" hexDigit hexDigit hexDigit hexDigit hexDigit |
                              "0010" hexDigit hexDigit hexDigit hexDigit
```

### 空语句

```
emptyStatement = ";"
```

### 常量

```
constant = fullIdent | ( [ "-" | "+" ] intLit ) | ( [ "-" | "+" ] floatLit ) |
                strLit | boolLit | MessageValue
```

`MessageValue` 定义在[文本格式语言规范](/reference/protobuf/textformat-spec#fields)中。

## syntax 声明

syntax 声明用于定义 Protobuf 版本。

```
syntax = "syntax" "=" ("'" "proto3" "'" | '"' "proto3" '"') ";"
```

示例：

```proto
syntax = "proto3";
```

## import 语句 {#import_statement}

import 语句用于导入另一个 .proto 文件的定义。

```
import = "import" [ "weak" | "public" ] strLit ";"
```

示例：

```proto
import public "other.proto";
```

## 包

package 声明符可用于防止协议消息（message）类型之间发生名称冲突。

```
package = "package" fullIdent ";"
```

示例：

```proto
package foo.bar;
```

## 选项

选项（option）可用于 proto 文件、消息、枚举和服务（service）中。选项可以是 Protobuf 预定义的选项，也可以是自定义选项。更多信息请参阅语言指南中的[选项](/programming-guides/proto3#options)。

```
option = "option" optionName  "=" constant ";"
optionName = ( ident | bracedFullIdent ) { "." ( ident | bracedFullIdent ) }
bracedFullIdent = "(" ["."] fullIdent ")"
optionNamePart = { ident | "(" ["."] fullIdent ")" }
```

示例：

```proto
option java_package = "com.example.foo";
```

## 字段

字段（field）是 Protobuf 消息的基本元素。字段可以是普通字段、oneof 字段或 map 字段。每个字段都有类型和字段编号（field number）。

```
type = "double" | "float" | "int32" | "int64" | "uint32" | "uint64"
      | "sint32" | "sint64" | "fixed32" | "fixed64" | "sfixed32" | "sfixed64"
      | "bool" | "string" | "bytes" | messageType | enumType
fieldNumber = intLit;
```

### 普通字段 {#normal_field}

每个字段都有类型、名称和字段编号，还可以有字段选项。

```
field = [ "repeated" | "optional" ] type fieldName "=" fieldNumber [ "[" fieldOptions "]" ] ";"
fieldOptions = fieldOption { ","  fieldOption }
fieldOption = optionName "=" constant
```

示例：

```proto
foo.Bar nested_message = 2;
repeated int32 samples = 4 [packed=true];
```

### oneof 与 oneof 字段 {#oneof_and_oneof_field}

oneof 由若干 oneof 字段和一个 oneof 名称组成。

```
oneof = "oneof" oneofName "{" { option | oneofField } "}"
oneofField = type fieldName "=" fieldNumber [ "[" fieldOptions "]" ] ";"
```

示例：

```proto
oneof foo {
    string name = 4;
    SubMessage sub_message = 9;
}
```

### map 字段 {#map_field}

map 字段具有键类型、值类型、名称和字段编号。键类型可以是任意整数类型或字符串类型。

```
mapField = "map" "<" keyType "," type ">" mapName "=" fieldNumber [ "[" fieldOptions "]" ] ";"
keyType = "int32" | "int64" | "uint32" | "uint64" | "sint32" | "sint64" |
          "fixed32" | "fixed64" | "sfixed32" | "sfixed64" | "bool" | "string"
```

示例：

```proto
map<string, Project> projects = 3;
```

## 保留

reserved 语句声明本消息中一段不可使用的字段编号或字段名。

```
reserved = "reserved" ( ranges | strFieldNames ) ";"
ranges = range { "," range }
range =  intLit [ "to" ( intLit | "max" ) ]
strFieldNames = strFieldName { "," strFieldName }
strFieldName = "'" fieldName "'" | '"' fieldName '"'
```

示例：

```proto
reserved 2, 15, 9 to 11;
reserved "foo", "bar";
```

## 顶层定义 {#top_level_definitions}

### 枚举定义 {#enum_definition}

枚举定义由一个名称和一个枚举体组成。枚举体中可以包含选项、枚举值（enum fields）和 reserved 语句。

```
enum = "enum" enumName enumBody
enumBody = "{" { option | enumField | emptyStatement | reserved } "}"
enumField = ident "=" [ "-" ] intLit [ "[" enumValueOption { ","  enumValueOption } "]" ]";"
enumValueOption = optionName "=" constant
```

示例：

```proto
enum EnumAllowingAlias {
  option allow_alias = true;
  EAA_UNSPECIFIED = 0;
  EAA_STARTED = 1;
  EAA_RUNNING = 2 [(custom_option) = "hello world"];
}
```

### 消息定义 {#message_definition}

消息由消息名称和消息体组成。消息体中可以包含字段、嵌套枚举定义、嵌套消息定义、选项、oneof、map 字段和 reserved 语句。在同一个消息模式（schema）中，消息不能包含两个同名的字段。

```
message = "message" messageName messageBody
messageBody = "{" { field | enum | message | option | oneof | mapField |
reserved | emptyStatement } "}"
```

示例：

```proto
message Outer {
  option (my_option).a = true;
  message Inner {   // 第 2 层
    int64 ival = 1;
  }
  map<int32, string> my_map = 2;
}
```

消息中声明的任何实体都不得使用相互冲突的名称。以下所有写法均被禁止：

```
message MyMessage {
  optional string foo = 1;
  message foo {}
}

message MyMessage {
  optional string foo = 1;
  oneof foo {
    string bar = 2;
  }
}

message MyMessage {
  optional string foo = 1;
  enum E {
    foo = 0;
  }
}
```

### 服务定义 {#service_definition}

```
service = "service" serviceName "{" { option | rpc | emptyStatement } "}"
rpc = "rpc" rpcName "(" [ "stream" ] messageType ")" "returns" "(" [ "stream" ]
messageType ")" (( "{" {option | emptyStatement } "}" ) | ";")
```

示例：

```proto
service SearchService {
  rpc Search (SearchRequest) returns (SearchResponse);
}
```

## proto 文件 {#proto_file}

```
proto = [syntax] { import | package | option | topLevelDef | emptyStatement }
topLevelDef = message | enum | service
```

一个 .proto 文件示例：

```proto
syntax = "proto3";
import public "other.proto";
option java_package = "com.example.foo";
enum EnumAllowingAlias {
  option allow_alias = true;
  EAA_UNSPECIFIED = 0;
  EAA_STARTED = 1;
  EAA_RUNNING = 1;
  EAA_FINISHED = 2 [(custom_option) = "hello world"];
}
message Outer {
  option (my_option).a = true;
  message Inner {   // 第 2 层
    int64 ival = 1;
  }
  repeated Inner inner_message = 2;
  EnumAllowingAlias enum_field = 3;
  map<int32, string> my_map = 4;
}
```
