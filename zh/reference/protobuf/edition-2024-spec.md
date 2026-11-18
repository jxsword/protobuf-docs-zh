+++
title = "Protobuf 版次 2024 语言规范"
weight = 801
linkTitle = "2024 语言规范"
description = "Protobuf 语言版次 2024 的语言规范参考。"
type = "docs"
source_url = "https://protobuf.dev/reference/protobuf/edition-2024-spec/"
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

## 词法元素 {#lexical_elements}

### 字母与数字 {#letters_and_digits}

```
letter = "A" ... "Z" | "a" ... "z"
capitalLetter =  "A" ... "Z"
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
streamName = ident
messageType = [ "." ] { ident "." } messageName
enumType = [ "." ] { ident "." } enumName
groupName = capitalLetter { letter | decimalDigit | "_" }
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
strLitSingle = ( "'" { charValue } "'" ) | ( '"' { charValue } '"' )
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

## 版次

版次（edition）声明取代了旧有的 `syntax` 关键字，用于定义本文件所使用的版次。

```
edition = "edition" "=" [ ( "'" decimalLit "'" ) | ( '"' decimalLit '"' ) ] ";"
```

## import 语句 {#import_statement}

import 语句用于导入另一个 .proto 文件的定义。

```
import = "import" [ "public" | "option" ] strLit ";"
```

示例：

```proto
import public "other.proto";
import option "custom_option.proto";
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

选项（option）可用于 proto 文件、消息、枚举和服务（service）中。选项可以是 Protobuf 预定义的选项，也可以是自定义选项。更多信息请参阅语言指南中的[选项](/programming-guides/proto2#options)。选项还可用于控制[特性设置](/editions/features)。

```
option = "option" optionName  "=" constant ";"
optionName = ( ident | "(" ["."] fullIdent ")" )
```

示例如下：

```proto
option java_package = "com.example.foo";
option features.enum_type = CLOSED;
```

## 字段

字段（field）是 Protobuf 消息的基本元素。字段可以是普通字段、组（group）字段、oneof 字段或 map 字段。每个字段都有标签（label）、类型和字段编号（field number）。

```
label = [ "repeated" ]
type = "double" | "float" | "int32" | "int64" | "uint32" | "uint64"
      | "sint32" | "sint64" | "fixed32" | "fixed64" | "sfixed32" | "sfixed64"
      | "bool" | "string" | "bytes" | messageType | enumType
fieldNumber = intLit;
```

### 普通字段 {#normal_field}

每个字段都有标签、类型、名称和字段编号，还可以有字段选项。

```
field = [label] type fieldName "=" fieldNumber [ "[" fieldOptions "]" ] ";"
fieldOptions = fieldOption { ","  fieldOption }
fieldOption = optionName "=" constant
```

示例：

```proto
foo.bar nested_message = 2;
repeated int32 samples = 4 [packed=true];
```

### oneof 与 oneof 字段 {#oneof_and_oneof_field}

oneof 由若干 oneof 字段和一个 oneof 名称组成。oneof 字段没有标签。

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

map 字段具有键类型、值类型、名称和字段编号。键类型可以是任意整数类型或字符串类型。注意，键类型不能是枚举。

```
mapField = "map" "<" keyType "," type ">" mapName "=" fieldNumber [ "[" fieldOptions "]" ] ";"
keyType = "int32" | "int64" | "uint32" | "uint64" | "sint32" | "sint64" |
          "fixed32" | "fixed64" | "sfixed32" | "sfixed64" | "bool" | "string"
```

示例：

```proto
map<string, Project> projects = 3;
```

## 扩展与保留 {#extensions_and_reserved}

扩展（extension）与保留（reserved）是消息元素，用于声明一段字段编号或一组字段名。

### 扩展

扩展声明消息中的一段字段编号可供第三方扩展使用。其他人可以在自己的 .proto 文件中使用这些数字标签（tag）为你的消息类型声明新字段，而不必编辑原始文件。

```
extensions = "extensions" ranges ";"
ranges = range { "," range }
range =  intLit [ "to" ( intLit | "max" ) ]
```

示例：

```proto
extensions 100 to 199;
extensions 4, 20 to max;
```

### 保留

reserved 声明消息或枚举中一段不可使用的字段编号或字段名。

```
reserved = "reserved" ( ranges | reservedIdent ) ";"
fieldNames = fieldName { "," fieldName }
```

示例：

```proto
reserved 2, 15, 9 to 11;
reserved foo, bar;
```

## 顶层定义 {#top_level_definitions}

### 符号可见性 {#symbol_visibility}

部分消息和枚举定义可以通过标注来覆盖其默认的符号可见性。

这由 [`features.default_symbol_visibility`](/editions/features/#symbol-vis) 控制；符号可见性的进一步说明见 [export / local 关键字](/editions/overview/#export-local)。

```
symbolVisibility = "export" | "local"
```

### 枚举定义 {#enum_definition}

枚举定义由一个名称和一个枚举体组成。枚举体中可以包含选项、枚举值（enum fields）和 reserved 语句。

```
enum = [ symbolVisibility ] "enum" enumName enumBody
enumBody = "{" { option | enumField | emptyStatement | reserved } "}"
enumField = fieldName "=" [ "-" ] intLit [ "[" enumValueOption { ","  enumValueOption } "]" ]";"
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

消息由消息名称和消息体组成。消息体中可以包含字段、嵌套枚举定义、嵌套消息定义、extend 语句、扩展、组、选项、oneof、map 字段和 reserved 语句。在同一个消息模式（schema）中，消息不能包含两个同名的字段。

```
message = [ symbolVisibility ] "message" messageName messageBody
messageBody = "{" { field | enum | message | extend | extensions | group |
option | oneof | mapField | reserved | emptyStatement } "}"
```

示例：

```proto
message Outer {
  option (my_option).a = true;
  message Inner {   // 第 2 层
    required int64 ival = 1;
  }
  map<int32, string> my_map = 2;
  extensions 20 to 30;
}
```

消息中声明的任何实体都不得使用相互冲突的名称。以下所有写法均被禁止：

```
message MyMessage {
  string foo = 1;
  message foo {}
}

message MyMessage {
  string foo = 1;
  oneof foo {
    string bar = 2;
  }
}

message MyMessage {
  string foo = 1;
  extend Extendable {
    string foo = 2;
  }
}

message MyMessage {
  string foo = 1;
  enum E {
    foo = 0;
  }
}
```

### extend

如果同一 .proto 文件或已导入的 .proto 文件中的某个消息已经为扩展保留了一段区间，那么该消息就可以被扩展。

```
extend = "extend" messageType "{" {field | group} "}"
```

示例：

```proto
extend Foo {
  int32 bar = 126;
}
```

### 服务定义 {#service_definition}

```
service = "service" serviceName "{" { option | rpc | emptyStatement } "}"
rpc = "rpc" rpcName "(" [ "stream" ] messageType ")" "returns" "(" [ "stream" ]
messageType ")" (( "{" { option | emptyStatement } "}" ) | ";" )
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
topLevelDef = message | enum | extend | service
```

一个 .proto 文件示例：

```proto
edition = "2024";
import public "other.proto";
import option "custom_option.proto";
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
    int64 ival = 1 [features.field_presence = LEGACY_REQUIRED];
  }
  repeated Inner inner_message = 2;
  EnumAllowingAlias enum_field = 3;
  map<int32, string> my_map = 4;
  extensions 20 to 30;
  reserved reserved_field;
}
message Foo {
  message GroupMessage {
    bool a = 1;
  }
  GroupMessage groupmessage = [features.message_encoding = DELIMITED];
}
```
