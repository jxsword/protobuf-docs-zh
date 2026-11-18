+++
title = "PHP 生成代码指南"
weight = 730
linkTitle = "生成代码指南"
description = "描述 Protobuf 编译器为任意给定协议定义所生成的 PHP 代码。"
type = "docs"
source_url = "https://protobuf.dev/reference/php/php-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

阅读本文档之前，你应当先阅读 [proto3 语言指南](/programming-guides/proto3)或[版次语言指南](/programming-guides/editions)。请注意，Protobuf 编译器目前针对 PHP 仅支持 proto3 和版次的代码生成。

## 编译器调用 {#invocation}

使用 `--php_out=` 命令行标志调用 Protobuf 编译器时，编译器会生成 PHP 输出。`--php_out=` 选项的参数是你希望编译器写入 PHP 输出的目录。为了符合 PSR-4 规范，编译器会创建一个与 proto 文件（proto file）中定义的包（package）相对应的子目录。此外，对于 proto 文件输入中的每个消息（message），编译器都会在该包的子目录下创建一个单独的文件。消息输出文件的名称由三部分组成：

-   基础目录：proto 路径（通过 `--proto_path=` 或 `-I` 命令行标志指定）会被替换为输出路径（通过 `--php_out=` 标志指定）。
-   子目录：包名中的 `.` 会被替换为操作系统的目录分隔符。包名的每个组成部分都会首字母大写。
-   文件：消息名后追加 `.php`。

举例来说，假设你按如下方式调用编译器：

```shell
protoc --proto_path=src --php_out=build/gen src/example.proto
```

而 `src/example.proto` 的定义如下：

```proto
edition = "2023";
package foo.bar;
message MyMessage {}
```

编译器会读取文件 `src/foo.proto`，并生成输出文件 `build/gen/Foo/Bar/MyMessage.php`。如有必要，编译器会自动创建目录 `build/gen/Foo/Bar`，但*不会*创建 `build` 或 `build/gen`；这两个目录必须已经存在。

## 包 {#package}

默认情况下，`.proto` 文件中定义的包名会用于为生成的 PHP 类构建模块结构。给定如下文件：

```proto
package foo.bar;

message MyMessage {}
```

协议编译器会生成名为 `Foo\Bar\MyMessage` 的输出类。

### 命名空间选项 {#namespace-options}

编译器支持通过附加选项来定义 PHP 命名空间（namespace）和元数据命名空间。定义这些选项后，它们将用于生成模块结构和命名空间。给定如下选项：

```proto
package foo.bar;
option php_namespace = "baz\\qux";
option php_metadata_namespace = "Foo";
message MyMessage {}
```

协议编译器会生成名为 `baz\qux\MyMessage` 的输出类。该类将使用命名空间 `namespace baz\qux`。

协议编译器会生成名为 `Foo\Metadata` 的元数据类。该类将使用命名空间 `namespace Foo`。

*生成的选项区分大小写。默认情况下，包名会被转换为帕斯卡命名（Pascal case）形式。*

## 消息 {#message}

给定如下简单的消息声明：

```proto
message Foo {
  int32 int32_value = 1;
  string string_value = 2;
  repeated int32 repeated_int32_value = 3;
  map<int32, int32> map_int32_int32_value = 4;
}
```

Protobuf 编译器会生成一个名为 `Foo` 的 PHP 类。该类继承自公共基类 `Google\Protobuf\Internal\Message`，后者提供了对你的消息类型进行编码和解码的方法，如下例所示：

```php
$from = new Foo();
$from->setInt32Value(1);
$from->setStringValue('a');
$from->getRepeatedInt32Value()[] = 1;
$from->getMapInt32Int32Value()[1] = 1;
$data = $from->serializeToString();
$to = new Foo();
try {
  $to->mergeFromString($data);
} catch (Exception $e) {
  // 处理无效数据导致的解析错误。
  ...
}
```

你*不应*自行创建 `Foo` 的子类。生成的类并非为子类化而设计，否则可能导致“脆弱基类（fragile base class）”问题。

由于 PHP 不支持嵌套类，嵌套消息会生成同名的 PHP 类，类名以包含它的消息名称为前缀，并用下划线分隔。举例来说，如果你的 `.proto` 中有如下定义：

```proto
message TestMessage {
  message NestedMessage {
    int32 a = 1;
  }
}
```

编译器会生成如下类：

```php
// PHP 不支持嵌套类。
class TestMessage_NestedMessage {
  public function __construct($data = NULL) {...}
  public function getA() {...}
  public function setA($var) {...}
}
```

如果消息类名是保留字（例如 `Empty`），则会在类名前加上前缀 `PB`：

```php
class PBEmpty {...}
```

我们还提供了文件级选项 `php_class_prefix`。如果指定了该选项，它会加在所有生成的消息类名前面。

## 字段

对于消息类型中的每个字段（field），Protobuf 编译器会生成一组用于设置和获取该字段的访问器（accessor）方法。访问器方法以 `snake_case` 形式的字段名转换为 `PascalCase` 后的名称命名。因此，给定字段 `field_name`，对应的访问器方法就是 `getFieldName` 和 `setFieldName`。

```php
// 字段声明：optional MyEnum optional_enum
$m->getOptionalEnum();
$m->setOptionalEnum(MyEnum->FOO);
$m->hasOptionalEnum();
$m->clearOptionalEnum();

// 字段声明：MyEnum implicit_enum
$m->getImplicitEnum();
$m->setImplicitEnum(MyEnum->FOO);
```

每当你设置一个字段时，都会根据该字段声明的类型对值（value）进行类型检查。如果值的类型错误（或超出范围），就会抛出异常。默认情况下，允许在整数、浮点数和数字字符串之间进行类型转换（例如，为字段赋值或向可重复字段添加元素时）。不允许的转换包括所有涉及数组或对象的转换。浮点数到整数的溢出转换行为未定义。

每种 Protobuf 标量（scalar）类型对应的 PHP 类型，可参见[标量值类型表](/programming-guides/proto3#scalar)。

### `has...` 与 `clear...`

对于具有显式存在性（explicit presence）的字段，编译器会生成 `has...()` 方法。如果字段已被设置，该方法返回 `true`。

编译器还会生成 `clear...()` 方法。该方法会取消设置该字段。调用该方法之后，`has...()` 将返回 `false`。

对于具有隐式存在性（implicit presence）的字段，编译器不会生成 `has...()` 或 `clear...()` 方法。对于这类字段，你可以通过将字段值与默认值（default value）进行比较，来检查字段是否已被设置。

### 单数消息字段 {#embedded_message}

对于消息类型的字段，编译器会生成与标量类型相同的访问器方法。

消息类型字段的默认值为 `null`，并且在访问该字段时不会自动创建。因此，你需要像下面这样显式创建子消息：

```php
$m = new MyMessage();
$m->setZ(new SubMessage());
$m->getZ()->setFoo(42);

$m2 = new MyMessage();
$m2->getZ()->setFoo(42);  // 会失败并抛出异常
```

你可以把任意实例赋给消息字段，即使该实例在其他地方也被引用（例如，作为另一个消息的字段值）。

### 可重复字段

Protobuf 编译器会为每个可重复字段生成一个特殊的 `RepeatedField`。举例来说，给定如下字段：

```proto
repeated int32 foo = 1;
```

借助生成的代码（generated code），你可以这样写：

```php
$m->getFoo()[] =1;
$m->setFoo($array);
```

### map 字段

Protobuf 编译器会为每个 map 字段生成一个 `MapField`。给定如下字段：

```proto
map<int32, int32> weight = 1;
```

借助生成的代码，你可以执行以下操作：

```php
$m->getWeight()[1] = 1;
```

## 枚举 {#enum}

PHP 没有原生枚举（enum），因此 Protobuf 编译器会转而为 `.proto` 文件中的每个枚举类型生成一个 PHP 类（与[消息](#message)一样），并为每个枚举值定义常量。给定如下枚举：

```proto
enum TestEnum {
  Default = 0;
  A = 1;
}
```

编译器会生成如下类：

```php
class TestEnum {
  const DEFAULT = 0;
  const A = 1;
}
```

与消息一样，嵌套枚举也会生成同名的 PHP 类，类名以包含它的消息名称为前缀，并用下划线分隔，因为 PHP 不支持嵌套类。

```php
class TestMessage_NestedEnum {...}
```

如果枚举类名或枚举值名是保留字（例如 `Empty`），则会在类名或值名前加上前缀 `PB`：

```php
class PBEmpty {
  const PBECHO = 0;
}
```

我们还提供了文件级选项 `php_class_prefix`。如果指定了该选项，它会加在所有生成的枚举类名前面。

## Oneof

对于 [oneof](/programming-guides/editions#oneof)，Protobuf 编译器会为 oneof 中的每个字段生成 `has` 和 `clear` 方法，还会生成一个特殊的访问器方法，让你可以得知当前设置的是哪个 oneof 字段（如果有的话）。给定如下消息：

```proto
message TestMessage {
  oneof test_oneof {
    int32 oneof_int32 = 1;
    int64 oneof_int64 = 2;
  }
}
```

编译器会生成如下字段和特殊方法：

```php
class TestMessage {
  private oneof_int32;
  private oneof_int64;
  public function getOneofInt32();
  public function setOneofInt32($var);
  public function getOneofInt64();
  public function setOneofInt64($var);
  public function getTestOneof();  // 返回字段名
}
```

访问器方法的名称基于 oneof 的名称，返回一个字符串，表示 oneof 中当前被设置的字段。如果 oneof 未被设置，该方法会返回空字符串。

当你设置 oneof 中的某个字段时，oneof 中的所有其他字段会被自动清除。如果想在一个 oneof 中设置多个字段，必须分别用单独的语句进行设置。

```php
$m = new TestMessage();
$m->setOneofInt32(42); // $m->hasOneofInt32() 为 true
$m->setOneofInt64(123); // $m->hasOneofInt32() 现在为 false
```
