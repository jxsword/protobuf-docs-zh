+++
title = "Ruby 生成代码指南"
weight = 780
linkTitle = "生成代码指南"
description = "描述 Protobuf 编译器为任意给定协议定义所生成的消息对象的 API。"
type = "docs"
source_url = "https://protobuf.dev/reference/ruby/ruby-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

阅读本文档之前，你应当先阅读 [proto2](/programming-guides/proto2)、[proto3](/programming-guides/proto3) 或 [版次（editions）](/programming-guides/editions) 的语言指南（language guide）。

## 编译器调用 {#invocation}

使用 `--ruby_out=` 命令行标志调用 Protobuf 编译器时，编译器会生成 Ruby 输出。`--ruby_out=` 选项的参数是你希望编译器写入 Ruby 输出的目录。编译器会为每个输入的 `.proto` 文件创建一个 `.rb` 文件。输出文件的名称由 `.proto` 文件的名称经过以下两处改动得到：

-   扩展名（`.proto`）被替换为 `_pb.rb`。
-   proto 路径（通过 `--proto_path=` 或 `-I` 命令行标志指定）被替换为输出路径（通过 `--ruby_out=` 标志指定）。

举例来说，假设你按如下方式调用编译器：

```shell
protoc --proto_path=src --ruby_out=build/gen src/foo.proto src/bar/baz.proto
```

编译器会读取文件 `src/foo.proto` 和 `src/bar/baz.proto`，并生成两个输出文件：`build/gen/foo_pb.rb` 和 `build/gen/bar/baz_pb.rb`。如有必要，编译器会自动创建目录 `build/gen/bar`，但*不会*创建 `build` 或 `build/gen`；这两个目录必须已经存在。

## 包 {#package}

`.proto` 文件中定义的包（package）名会用于为生成的消息（message）构建模块结构。给定如下文件：

```proto
package foo_bar.baz;

message MyMessage {}
```

协议编译器会生成名为 `FooBar::Baz::MyMessage` 的输出消息。

不过，如果 `.proto` 文件中包含 `ruby_package` 选项（option），如下所示：

```proto
option ruby_package = "Foo::Bar";
```

那么生成的输出会优先采用 `ruby_package` 选项，并生成 `Foo::Bar::MyMessage`。

## 消息 {#message}

给定如下简单的消息声明：

```proto
message Foo {}
```

Protobuf 编译器会生成一个名为 `Foo` 的类。生成的类派生自 Ruby 的 `Object` 类（proto 没有公共基类）。与 C++ 和 Java 不同，Ruby 生成代码（generated code）不受 `.proto` 文件中 `optimize_for` 选项的影响；实际上，所有 Ruby 代码都相当于针对代码大小进行了优化。

你*不应*自行创建 `Foo` 的子类。生成的类并非为子类化而设计，否则可能导致“脆弱基类（fragile base class）”问题。

Ruby 消息类会为每个字段（field）定义访问器（accessor），还提供以下标准方法：

-   `Message#dup`、`Message#clone`：对当前消息执行浅拷贝，并返回新副本。
-   `Message#==`：对两个消息执行深度相等性比较。
-   `Message#hash`：计算消息值的浅哈希。
-   `Message#to_hash`、`Message#to_h`：将对象转换为 Ruby 的 `Hash` 对象。仅转换顶层消息。
-   `Message#inspect`：返回表示当前消息的人类可读字符串。
-   `Message#[]`、`Message#[]=`：按字符串名称获取或设置字段。将来这很可能还会用于获取/设置扩展（extension）。

消息类还将以下方法定义为静态方法。（总的来说，我们更倾向于使用静态方法，因为普通方法可能会与你 .proto 文件中定义的字段名（field name）冲突。）

-   `Message.decode(str)`：解码此消息类型的二进制 Protobuf 数据，并放入一个新实例返回。
-   `Message.encode(proto)`：将此类的消息对象序列化（serialization）为二进制字符串。
-   `Message.decode_json(str)`：解码此消息的 JSON 文本字符串，并放入一个新实例返回。
-   `Message.encode_json(proto)`：将此类的消息对象序列化为 JSON 文本字符串。
-   `Message.descriptor`：返回此消息的 `Google::Protobuf::Descriptor` 对象。

创建消息时，你可以在构造函数中便捷地初始化字段。下面是构造和使用消息的示例：

```ruby
message = MyMessage.new(int_field: 1,
                        string_field: "String",
                        repeated_int_field: [1, 2, 3, 4],
                        submessage_field: MyMessage::SubMessage.new(foo: 42))
serialized = MyMessage.encode(message)

message2 = MyMessage.decode(serialized)
raise unless message2.int_field == 1
```

### 嵌套类型

消息可以声明在另一个消息内部。例如：

```proto
message Foo {
  message Bar { }
}
```

此时，`Bar` 类会声明为 `Foo` 内部的一个类，因此你可以通过 `Foo::Bar` 来引用它。

## 字段

消息类型中的每个字段都有用于设置和获取该字段的访问器方法。因此，给定字段 `foo`，你可以这样写：

```ruby
message.foo = get_value()
print message.foo
```

每当你设置一个字段时，都会依据该字段声明的类型对值进行类型检查。如果值的类型错误（或超出范围），就会抛出异常。

### 单数字段

对于单数（singular）原始字段（数字、字符串和布尔值），你赋给字段的值应当类型正确，并且必须处于适当的范围内：

-   **数字类型**：值应当是 `Fixnum`、`Bignum` 或 `Float`。你赋的值必须能在目标类型中精确表示。因此，把 `1.0` 赋给 int32 字段是可以的，但赋 `1.2` 则不行。
-   **布尔字段**：值必须是 `true` 或 `false`。其他任何值都不会被隐式转换为 true/false。
-   **bytes 字段**：赋的值必须是 `String` 对象。Protobuf 库会复制该字符串，将其转换为 ASCII-8BIT 编码（encoding），并冻结它。
-   **字符串字段**：赋的值必须是 `String` 对象。Protobuf 库会复制该字符串，将其转换为 UTF-8 编码，并冻结它。

Protobuf 不会自动调用 `#to_s`、`#to_i` 等方法来完成类型转换；如有必要，你应当先自行转换值。

#### 检查存在性

显式字段存在性（field presence）由 `field_presence` 特性（在版次中）、`optional` 关键字（在 proto2/proto3 中）以及字段类型（消息和 oneof 字段始终具有显式存在性）决定。当字段具有存在性时，你可以通过调用生成的 `has_...?` 方法来检查消息上是否已设置该字段。设置任何值&mdash;哪怕是默认值（default value）&mdash;都会将该字段标记为已设置。字段可以通过调用另一个生成的 `clear_...` 方法来清除。

例如，对于带有 int32 字段 `foo` 的消息 `MyMessage`：

```proto
message MyMessage {
  int32 foo = 1;
}
```

`foo` 的存在性可以按如下方式检查：

```ruby
m = MyMessage.new
raise if m.has_foo?
m.foo = 0
raise unless m.has_foo?
m.clear_foo
raise if m.has_foo?
```

### 单数消息字段 {#embedded_message}

无论是否标记为 `optional`，子消息（submessage）字段始终具有存在性。未设置的子消息字段返回 `nil`，因此你总能判断该消息是否被显式设置过。要清除子消息字段，请将其值显式设置为 `nil`。

```ruby
if message.submessage_field.nil?
  puts "Submessage field is unset."
else
  message.submessage_field = nil
  puts "Cleared submessage field."
end
```

除了比较和赋值 `nil` 之外，生成的消息还提供 `has_...` 和 `clear_...` 方法，它们的行为与基本类型的同名方法一致：

```ruby
if !message.has_submessage_field?
  puts "Submessage field is unset."
else
  message.clear_submessage_field
  raise if message.has_submessage_field?
  puts "Cleared submessage field."
end
```

赋值子消息时，它必须是类型正确的生成消息对象。

在赋值子消息时，可能会形成消息循环。例如：

```proto
// 文件 foo.proto
message RecursiveMessage {
  RecursiveMessage submessage = 1;
}

# 文件 test.rb
require 'foo'

message = RecursiveMessage.new
message.submessage = message
```

如果你尝试序列化它，库会检测到该循环并导致序列化失败。

### repeated 字段

repeated 字段用自定义类 `Google::Protobuf::RepeatedField` 来表示。该类的行为如同 Ruby 的 `Array`，并混入了 `Enumerable`。与普通的 Ruby 数组不同，`RepeatedField` 在构造时带有特定类型，并要求数组的所有成员都具有正确的类型。类型和范围的检查方式与消息字段相同。

```ruby
int_repeatedfield = Google::Protobuf::RepeatedField.new(:int32, [1, 2, 3])

raise unless !int_repeatedfield.empty?

# 抛出 TypeError。
int_repeatedfield[2] = "not an int32"

# 抛出 RangeError
int_repeatedfield[2] = 2**33

message.int32_repeated_field = int_repeatedfield

# 这是不允许的；普通 Ruby 数组不会像我们要求的那样强制类型检查。
message.int32_repeated_field = [1, 2, 3, 4]

# 这样可以，因为元素会被复制到类型安全的数组中。
message.int32_repeated_field += [1, 2, 3, 4]

# 无需重新赋值即可清空元素。
int_repeatedfield.clear
raise unless int_repeatedfield.empty?
```

对于包含消息的 repeated 字段，`Google::Protobuf::RepeatedField` 的构造函数支持一种带三个参数的变体：`:message`、子消息的类，以及要设置的值：

```ruby
first_message = MySubMessage.new(foo: 42)
second_message = MySubMessage.new(foo: 79)

repeated_field = Google::Protobuf::RepeatedField.new(
    :message,
    MySubMessage,
    [first_message, second_message]
)
message.sub_message_repeated_field = repeated_field
```

`RepeatedField` 类型支持与普通 Ruby `Array` 相同的全部方法。你可以使用 `repeated_field.to_a` 将其转换为普通的 Ruby 数组。

与单数字段不同，repeated 字段永远不会生成 `has_...?` 方法。

### map 字段

map 字段用一个行为如同 Ruby `Hash` 的特殊类（`Google::Protobuf::Map`）来表示。与普通的 Ruby 哈希不同，`Map` 在构造时带有键（key）和值（value）的特定类型，并要求 map 的所有键和值都具有正确的类型。类型和范围的检查方式与消息字段以及 `RepeatedField` 元素相同。

```ruby
int_string_map = Google::Protobuf::Map.new(:int32, :string)

# 返回 nil；该项不在 map 中。
print int_string_map[5]

# 抛出 TypeError，值应当是字符串
int_string_map[11] = 200

# 没问题。
int_string_map[123] = "abc"

message.int32_string_map_field = int_string_map
```

## 枚举 {#enum}

由于 Ruby 没有原生枚举（enum），我们会为每个枚举创建一个模块，并用常量来定义各枚举值。给定如下 `.proto` 文件：

```proto
message Foo {
  enum SomeEnum {
    VALUE_A = 0;
    VALUE_B = 5;
    VALUE_C = 1234;
  }
  SomeEnum bar = 1;
}
```

你可以像下面这样引用枚举值：

```ruby
print Foo::SomeEnum::VALUE_A  # => 0
message.bar = Foo::SomeEnum::VALUE_A
```

你可以给枚举字段赋一个数字或一个符号（symbol）。读回该值时，如果枚举值是已知的，得到的就是符号；如果未知，则是数字。

对于 proto3 所使用的 `OPEN` 枚举（即开放式枚举），任何整数值都可以赋给该枚举，即使这个值未在枚举中定义。

```ruby
message.bar = 0
puts message.bar.inspect  # => :VALUE_A
message.bar = :VALUE_B
puts message.bar.inspect  # => :VALUE_B
message.bar = 999
puts message.bar.inspect  # => 999

# 抛出异常：RangeError: Unknown symbol value for enum field.
message.bar = :UNDEFINED_VALUE

# 对枚举值进行分支判断很方便。
case message.bar
when :VALUE_A
  # ...
when :VALUE_B
  # ...
when :VALUE_C
  # ...
else
  # ...
end
```

枚举模块还定义了以下实用方法：

-   `Foo::SomeEnum.lookup(number)`：查找给定的数字并返回其名称，找不到则返回 `nil`。如果多个名称对应同一个数字，则返回最先定义的那个。
-   `Foo::SomeEnum.resolve(symbol)`：返回该枚举名称对应的数字，找不到则返回 `nil`。
-   `Foo::SomeEnum.descriptor`：返回此枚举的描述符（descriptor）。

## Oneof

给定一个带 oneof 的消息：

```proto
message Foo {
  oneof test_oneof {
     string name = 1;
     int32 serial_number = 2;
  }
}
```

与 `Foo` 对应的 Ruby 类会拥有名为 `name` 和 `serial_number` 的成员，它们带有与普通[字段](#fields)一样的访问器方法。不过，与普通字段不同的是，一个 oneof 中同一时间最多只能设置一个字段，因此设置其中一个字段会清除其余字段。

```ruby
message = Foo.new

# 字段均为默认值。
raise unless message.name == ""
raise unless message.serial_number == 0
raise unless message.test_oneof == nil

message.name = "Bender"
raise unless message.name == "Bender"
raise unless message.serial_number == 0
raise unless message.test_oneof == :name

# 设置 serial_number 会清除 name。
message.serial_number = 2716057
raise unless message.name == ""
raise unless message.test_oneof == :serial_number

# 将 serial_number 设置为 nil 会清除该 oneof。
message.serial_number = nil
raise unless message.test_oneof == nil
```

对于 proto2 消息，oneof 成员还各自拥有独立的 `has_...?` 方法：

```ruby
message = Foo.new

raise unless !message.has_test_oneof?
raise unless !message.has_name?
raise unless !message.has_serial_number?
raise unless !message.has_test_oneof?

message.name = "Bender"
raise unless message.has_test_oneof?
raise unless message.has_name?
raise unless !message.has_serial_number?
raise unless !message.has_test_oneof?

```
