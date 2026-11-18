+++
title = "Python 生成代码指南"
weight = 750
linkTitle = "生成代码指南"
description = "描述 Protobuf 编译器针对任意给定的协议定义确切生成哪些 Python 定义。"
type = "docs"
source_url = "https://protobuf.dev/reference/python/python-generated/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

proto2、proto3 与版次（edition）生成代码之间的任何差异都会重点标出——请注意，这些差异存在于本文档所描述的生成代码（generated code）中，而非基础消息（message）类/接口——后者在所有版本（version）中都是相同的。阅读本文档之前，请先阅读 [proto2 语言指南](/programming-guides/proto2)、[proto3 语言指南](/programming-guides/proto3)和/或 [版次语言指南](/programming-guides/editions)。

Python Protobuf 的实现与 C++ 和 Java 略有不同。在 Python 中，编译器只输出用于为生成的类构建描述符（descriptor）的代码，而真正的工作由一个 [Python 元类（metaclass）](https://docs.python.org/2.7/reference/datamodel#metaclasses) 完成。本文档描述的是应用该元类*之后*你所得到的东西。

## 编译器调用 {#invocation}

使用 `--python_out=` 命令行标志调用时，Protobuf 编译器会生成 Python 输出。`--python_out=` 选项（option）的参数是你希望编译器写入 Python 输出的目录。编译器会为每个输入的 `.proto` 文件创建一个 `.py` 文件。输出文件名的确定方法是取 `.proto` 文件的名称并做两处修改：

-   扩展名（`.proto`）会被替换为 `_pb2.py`。
-   proto 路径（由 `--proto_path=` 或 `-I` 命令行标志指定）会被替换为输出路径（由 `--python_out=` 标志指定）。

举例来说，假设你按如下方式调用编译器：

```shell
protoc --proto_path=src --python_out=build/gen src/foo.proto src/bar/baz.proto
```

编译器会读取 `src/foo.proto` 与 `src/bar/baz.proto` 两个文件，并生成两个输出文件：`build/gen/foo_pb2.py` 和 `build/gen/bar/baz_pb2.py`。必要时编译器会自动创建 `build/gen/bar` 目录，但*不会*创建 `build` 或 `build/gen`；这两个目录必须已经存在。

Protoc 还能够使用 `--pyi_out` 参数生成 Python 存根文件（`.pyi`）。

请注意，如果 `.proto` 文件或其路径中包含不能用于 Python 模块名的字符（例如连字符），这些字符会被替换为下划线。因此，文件 `foo-bar.proto` 会变成 Python 文件 `foo_bar_pb2.py`。

{{% alert title="Tip" color="note" %}} 输出 Python 代码时，Protobuf 编译器直接输出到 ZIP 归档文件的能力尤为方便，因为只要把这些归档文件放到 `PYTHONPATH` 中，Python 解释器就能直接从中读取。要输出到 ZIP 文件，只需提供一个以 `.zip` 结尾的输出位置。 {{% /alert %}}

{{% alert title="Note" color="note" %}}
`_pb2.py` 扩展名中的数字 2 表示 Protobuf 版本 2。版本 1 主要在 Google 内部使用，不过你也许能在 Protobuf 面世之前发布的其他 Python 代码中找到它的部分内容。由于 Python Protobuf 版本 2 的接口完全不同，而且 Python 没有能在编译期捕捉错误的类型检查，我们选择让版本号成为生成的 Python 文件名中一个醒目的组成部分。目前，proto2、proto3 和版次的生成文件都使用 `_pb2.py`。 {{% /alert %}}

## 包 {#package}

Protobuf 编译器生成的 Python 代码完全不受 `.proto` 文件中定义的包（package）名的影响。Python 包由目录结构来标识。

## 消息 {#message}

给定一个简单的消息声明：

```proto
message Foo {}
```

Protobuf 编译器会生成一个名为 `Foo` 的类，它继承自 [`google.protobuf.Message`](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message)。该类是一个具体类；没有任何抽象方法未实现。与 C++ 和 Java 不同，Python 生成代码不受 `.proto` 文件中 `optimize_for` 选项的影响；实际上，所有 Python 代码都是针对代码大小优化的。

如果消息的名称是 Python 关键字，那么它的类将只能通过 `getattr()` 访问，如[与 Python 关键字冲突的名称](#keyword-conflicts)一节所述。

你*不应*创建自己的 `Foo` 子类。生成的类并非为被子类化而设计，可能导致“脆弱基类（fragile base class）”问题。况且，实现继承本身就是糟糕的设计。

除了 `Message` 接口定义的成员，以及为嵌套字段（field）、消息和枚举（enum）类型生成的成员（下文描述）之外，Python 消息类没有其他特别的公有成员。`Message` 提供了一些方法，可用于检查、操作、读取或写入整个消息，包括从二进制字符串解析（parse）以及向二进制字符串序列化（serialization）。除这些方法之外，`Foo` 类还定义了以下静态方法：

-   `FromString(s)`：返回一个新的消息实例，由给定字符串反序列化（deserialization）而来。

请注意，你还可以使用 [`text_format`](https://googleapis.dev/python/protobuf/latest/google/protobuf/text_format.html) 模块来处理文本格式（text format）的协议消息：例如，`Merge()` 方法可以让你把一个消息的 ASCII 表示合并到现有消息中。

### 嵌套类型 {#nested-types}

消息可以声明在另一个消息内部。例如：

```proto
message Foo {
  message Bar {}
}
```

在这种情况下，`Bar` 类会被声明为 `Foo` 的静态成员，因此你可以通过 `Foo.Bar` 来引用它。

## 知名类型 {#wkt}

Protobuf 提供了许多[知名类型（well-known types）](/reference/protobuf/google.protobuf)，你可以在自己的 .proto 文件中将它们与自己的消息类型一起使用。一些 WKT 消息除了常规的 Protobuf 消息方法之外还有特殊方法，因为它们同时继承自 [`google.protobuf.Message`](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message) 和一个 WKT 类。

### Any {#any}

对于 Any 消息，你可以调用 `Pack()` 将指定的消息打包进当前 Any 消息，或者调用 `Unpack()` 将当前 Any 消息解包到指定的消息中。例如：

```python
any_message.Pack(message)
any_message.Unpack(message)
```

`Unpack()` 还会将传入消息对象的描述符与已存储的描述符进行比对，如果二者不匹配则返回 `False`，并且不会尝试任何解包操作；否则返回 `True`。

你还可以调用 `Is()` 方法来检查 Any 消息是否表示给定的 Protobuf 消息类型。例如：

```python
assert any_message.Is(message.DESCRIPTOR)
```

使用 `TypeName()` 方法可以获取内层消息的 Protobuf 类型名称。

### Timestamp {#timestamp}

Timestamp 消息可以使用 `ToJsonString()`/`FromJsonString()` 方法与 RFC 3339 日期字符串格式（JSON 字符串）相互转换。例如：

```python
timestamp_message.FromJsonString("1970-01-01T00:00:00Z")
assert timestamp_message.ToJsonString() == "1970-01-01T00:00:00Z"
```

你也可以调用 `GetCurrentTime()` 用当前时间填充 Timestamp 消息：

```python
timestamp_message.GetCurrentTime()
```

要在自纪元（epoch）起的其他时间单位之间进行转换，你可以调用 `ToNanoseconds(), FromNanoseconds(), ToMicroseconds(), FromMicroseconds(), ToMilliseconds(), FromMilliseconds(), ToSeconds()` 或 `FromSeconds()`。生成代码还提供 `ToDatetime()` 与 `FromDatetime()` 方法，用于在 Python datetime 对象和 Timestamp 之间转换。例如：

```python
timestamp_message.FromMicroseconds(-1)
assert timestamp_message.ToMicroseconds() == -1
dt = datetime(2016, 1, 1)
timestamp_message.FromDatetime(dt)
self.assertEqual(dt, timestamp_message.ToDatetime())
```

### Duration {#duration}

Duration 消息拥有与 Timestamp 相同的方法，可在 JSON 字符串与其他时间单位之间转换。要在 timedelta 与 Duration 之间转换，你可以调用 `ToTimedelta()` 或 `FromTimedelta`。例如：

```python
duration_message.FromNanoseconds(1999999999)
td = duration_message.ToTimedelta()
assert td.seconds == 1
assert td.microseconds == 999999
```

### FieldMask {#fieldmask}

FieldMask 消息可以使用 `ToJsonString()`/`FromJsonString()` 方法与 JSON 字符串相互转换。此外，FieldMask 消息还有以下方法：

-   `IsValidForDescriptor(message_descriptor)`：检查 FieldMask 对消息描述符是否有效。
-   `AllFieldsFromDescriptor(message_descriptor)`：获取消息描述符的所有直接字段并填入 FieldMask。
-   `CanonicalFormFromMask(mask)`：将 FieldMask 转换为规范形式（canonical form）。
-   `Union(mask1, mask2)`：将两个 FieldMask 合并到当前 FieldMask 中。
-   `Intersect(mask1, mask2)`：将两个 FieldMask 求交集后存入当前 FieldMask 中。
-   `MergeMessage(source, destination, replace_message_field=False, replace_repeated_field=False)`：把 FieldMask 中指定的字段从 source 合并到 destination。

### Struct {#struct}

Struct 消息让你可以直接获取和设置其中的条目。例如：

```python
struct_message["key1"] = 5
struct_message["key2"] = "abc"
struct_message["key3"] = True
```

要获取或创建列表或 Struct，可以调用 `get_or_create_list()`/`get_or_create_struct()`。例如：

```python
struct.get_or_create_struct("key4")["subkey"] = 11.0
struct.get_or_create_list("key5")
```

### ListValue {#listvalue}

ListValue 消息的行为类似一个 Python 序列，让你可以执行以下操作：

```python
list_value = struct_message.get_or_create_list("key")
list_value.extend([6, "seven", True, None])
list_value.append(False)
assert len(list_value) == 5
assert list_value[0] == 6
assert list_value[1] == "seven"
assert list_value[2] == True
assert list_value[3] == None
assert list_Value[4] == False
```

要添加 ListValue/Struct，可以调用 `add_list()`/`add_struct()`。例如：

```python
list_value.add_struct()["key"] = 1
list_value.add_list().extend([1, "two", True])
```

## 字段 {#fields}

对于消息类型中的每个字段，对应的类都有一个与该字段同名的属性（property）。你如何操作该属性取决于它的类型。

除了属性之外，编译器还会为每个字段生成一个包含其字段编号（field number）的整型常量。常量名是转换为大写的字段名再加上 `_FIELD_NUMBER`。例如，给定字段 `int32 foo_bar = 5;`，编译器会生成常量 `FOO_BAR_FIELD_NUMBER = 5`。

如果字段的名称是 Python 关键字，那么它的属性将只能通过 `getattr()` 和 `setattr()` 访问，如[与 Python 关键字冲突的名称](#keyword-conflicts)一节所述。

Protobuf 定义了两种字段存在性（field presence）模式：`explicit`（显式存在性，explicit presence）和 `implicit`（隐式存在性，implicit presence）。下面各节分别描述这两种模式。

### 具有显式存在性的单数字段 {#singular-explicit}

具有 `explicit` 存在性的单数（singular）字段始终能够区分“字段未设置”与“字段被设置为其默认值（default value）”这两种情况。

如果你有一个任意非消息类型的单数字段 `foo`，就可以像操作普通字段一样操作字段 `foo`。例如，如果 `foo` 的类型是 `int32`，你可以这样写：

```python
message.foo = 123
print(message.foo)
```

请注意，把 `foo` 设置为类型错误的值会抛出 `TypeError`。

在未设置的状态下读取 `foo` 时，得到的值是该字段的默认值。要检查 `foo` 是否已设置，或者清除 `foo` 的值，必须调用 [`Message`](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message) 接口的 `HasField()` 或 `ClearField()` 方法。例如：

```python
assert not message.HasField("foo")
message.foo = 123
assert message.HasField("foo")
message.ClearField("foo")
assert not message.HasField("foo")
```

在版次中，字段默认具有 `explicit` 存在性。下面是版次 `.proto` 文件中 `explicit` 字段的一个示例：

```proto
edition = "2023";
message MyMessage {
  int32 foo = 1;
}
```

### 具有隐式存在性的单数字段 {#singular-implicit}

具有 `implicit` 存在性的单数字段没有 `HasField()` 方法。`implicit` 字段始终处于“已设置”状态，读取该字段总是会返回一个值。读取尚未被赋值的 `implicit` 字段将返回该类型的默认值。

如果你有一个任意非消息类型的单数字段 `foo`，就可以像操作普通字段一样操作字段 `foo`。例如，如果 `foo` 的类型是 `int32`，你可以这样写：

```python
message.foo = 123
print(message.foo)
```

请注意，把 `foo` 设置为类型错误的值会抛出 `TypeError`。

在未设置的状态下读取 `foo` 时，得到的值是该字段的默认值。要清除 `foo` 的值并将其重置为该类型的默认值，可以调用 [`Message`](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message) 接口的 `ClearField()` 方法。例如：

```python
message.foo = 123
message.ClearField("foo")
```

### 单数消息字段 {#embedded_message}

消息类型的工作方式略有不同。你不能为内嵌消息字段赋值。相反，为子消息内的任何字段赋值，都意味着设置了父消息中的该消息字段。子消息始终具有[显式存在性](#fields-with-explicit-presence)，因此你还可以使用父消息的 `HasField()` 方法来检查消息类型字段的值是否已被设置。

举例来说，假设你有如下 `.proto` 定义：

```proto
edition = "2023";
message Foo {
  Bar bar = 1;
}
message Bar {
  int32 i = 1;
}
```

你*不能*这样做：

```python
foo = Foo()
foo.bar = Bar()  # 错误！
```

相反，要设置 `bar`，你只需直接为 `bar` 内的某个字段赋值——瞬间，`foo` 就拥有了一个 `bar` 字段：

```python
foo = Foo()
assert not foo.HasField("bar")
foo.bar.i = 1
assert foo.HasField("bar")
assert foo.bar.i == 1
foo.ClearField("bar")
assert not foo.HasField("bar")
assert foo.bar.i == 0  # 默认值
```

类似地，你还可以使用 [`Message`](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message) 接口的 `CopyFrom()` 方法来设置 `bar`。这会从另一个与 `bar` 同类型的消息中复制所有值。

```python
foo.bar.CopyFrom(baz)
```

请注意，仅仅读取 `bar` 内的字段并*不会*设置该字段：

```python
foo = Foo()
assert not foo.HasField("bar")
print(foo.bar.i)  # 打印 i 的默认值
assert not foo.HasField("bar")
```

如果你需要在一个没有任何可设置或想设置字段的消息上置起“has”位（hasbit），可以使用 `SetInParent()` 方法。

```python
foo = Foo()
assert not foo.HasField("bar")
foo.bar.SetInParent()  # 将 Foo.bar 设置为一个默认的 Bar 消息
assert foo.HasField("bar")
```

### 可重复字段 {#repeated-fields}

可重复字段分为三类：标量（scalar）、枚举和消息。映射（map）字段和 oneof 字段不能是可重复的。

### 可重复标量与枚举字段 {#repeated-scalar}

可重复字段表现为一个行为类似 Python 序列的对象。与内嵌消息一样，你不能直接为该字段赋值，但可以对它进行操作。例如，给定以下消息定义：

```proto
message Foo {
  repeated int32 nums = 1;
}
```

你可以执行以下操作：

```python
foo = Foo()
foo.nums.append(15)        # 追加一个值
foo.nums.extend([32, 47])  # 追加整个列表

assert len(foo.nums) == 3
assert foo.nums[0] == 15
assert foo.nums[1] == 32
assert foo.nums == [15, 32, 47]

foo.nums[:] = [33, 48]     # 整体赋值为一个列表
assert foo.nums == [33, 48]

foo.nums[1] = 56    # 重新赋一个值
assert foo.nums[1] == 56
for i in foo.nums:  # 循环并打印
  print(i)
del foo.nums[:]     # 清空列表（与在 Python 列表中的用法完全一样）
```

除使用 Python 的 `del` 之外，[`Message`](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message) 接口的 `ClearField()` 方法也同样可用。

用索引取值时，你可以使用负数，例如用 `-1` 获取列表中的最后一个元素。如果索引越界，你会得到 `IndexError: list index out of range`。

### 可重复消息字段 {#repeated-message-fields}

可重复消息字段的工作方式与可重复标量字段类似。不过，对应的 Python 对象还有一个 `add()` 方法，它会创建一个新的消息对象，将其追加到列表中，并返回给调用者去填充。此外，该对象的 `append()` 方法会先对给定消息制作一个**副本**，再把副本追加到列表中。这样做是为了让消息始终由父消息持有，从而避免循环引用，以及可变数据结构被多个所有者持有时可能出现的其他混乱。类似地，该对象的 `extend()` 方法会追加整个消息列表，但会对列表中的每条消息制作一个**副本**。

例如，给定以下消息定义：

```proto
edition = "2023";
message Foo {
  repeated Bar bars = 1;
}
message Bar {
  int32 i = 1;
  int32 j = 2;
}
```

你可以执行以下操作：

```python
foo = Foo()
bar = foo.bars.add()        # 添加一个 Bar 然后修改
bar.i = 15
foo.bars.add().i = 32       # 添加并同时修改
new_bar = Bar()
new_bar.i = 40
another_bar = Bar()
another_bar.i = 57
foo.bars.append(new_bar)        # 使用 append() 进行复制
foo.bars.extend([another_bar])  # 使用 extend() 进行复制

assert len(foo.bars) == 4
assert foo.bars[0].i == 15
assert foo.bars[1].i == 32
assert foo.bars[2].i == 40
assert foo.bars[2] == new_bar      # 追加的消息相等，
assert foo.bars[2] is not new_bar  # 但它是一个副本！
assert foo.bars[3].i == 57
assert foo.bars[3] == another_bar      # extend 追加的消息相等，
assert foo.bars[3] is not another_bar  # 但它是一个副本！

foo.bars[1].i = 56    # 修改单个元素
assert foo.bars[1].i == 56
for bar in foo.bars:  # 循环并打印
  print(bar.i)
del foo.bars[:]       # 清空列表

# add() 还会把关键字参数转发给具体类。
# 例如，你可以这样写：

foo.bars.add(i=12, j=13)

# 初始化器也会把关键字参数转发给具体类。
# 例如：

foo = Foo(             # 创建 Foo
  bars=[               # 把它的 bars 字段设为一个列表，
    Bar(i=15, j=17),   # 其中每个列表成员也会在创建时一并初始化。
    Bar(i=32),
    Bar(i=47, j=77),
  ]
)

assert len(foo.bars) == 3
assert foo.bars[0].i == 15
assert foo.bars[0].j == 17
assert foo.bars[1].i == 32
assert foo.bars[2].i == 47
assert foo.bars[2].j == 77
```

与可重复标量字段不同，可重复消息字段**不**支持对元素赋值（即 [`__setitem__`](https://docs.python.org/3/reference/datamodel#object.__setitem__)）。例如：

```python
foo = Foo()
foo.bars.add(i=3)
# 错误！
foo.bars[0] = Bar(i=15)  # 会抛出异常
# 错误！
foo.bars[:] = [Bar(i=15), Bar(i=17)]  # 同样会抛出异常
# 错误！
# AttributeError: Cannot delete field attribute（无法删除字段属性）
del foo.bars
# 正确
del foo.bars[:]
foo.bars.extend([Bar(i=15), Bar(i=17)])
```

### 组（proto2） {#groups-proto2}

**请注意，组（group）已弃用（deprecated），创建新的消息类型时不应再使用它——请改用嵌套消息类型（proto2、proto3）或[长度限定字段（delimited fields）](/editions/features#message_encoding)（版次）。**

组将一个嵌套消息类型和一个字段合并为一条声明，并为该消息使用不同的[线路格式（wire format）](/programming-guides/encoding)。生成的消息与组同名。生成的字段名是该组名称的**小写**形式。

例如，除线路格式外，下面两个消息定义是等价的：

```proto
// 版本 1：使用组
message SearchResponse {
  repeated group SearchResult = 1 {
    optional string url = 1;
  }
}
// 版本 2：不使用组
message SearchResponse {
  message SearchResult {
    optional string url = 1;
  }
  repeated SearchResult searchresult = 1;
}
```

组可以是 `required`、`optional` 或 `repeated`。required 或 optional 组使用与普通单数消息字段相同的 API 来操作。repeated 组使用与普通可重复消息字段相同的 API 来操作。

例如，给定上面的 `SearchResponse` 定义，你可以执行以下操作：

```python
resp = SearchResponse()
resp.searchresult.add(url="https://blog.google")
assert resp.searchresult[0].url == "https://blog.google"
assert resp.searchresult[0] == SearchResponse.SearchResult(url="https://blog.google")
```

### 映射字段 {#map-fields}

给定以下消息定义：

```proto
message MyMessage {
  map<int32, int32> mapfield = 1;
}
```

为映射字段生成的 Python API 就像一个 Python `dict`：

```python
# 向映射赋值
m.mapfield[5] = 10

# 从映射读取值
m.mapfield[5]

# 遍历映射中的键
for key in m.mapfield:
  print(key)
  print(m.mapfield[key])

# 测试某个键是否在映射中：
if 5 in m.mapfield:
  print(“Found!”)

# 从映射中删除键。
del m.mapfield[key]
```

与[内嵌消息字段](#embedded_message)一样，消息不能直接赋给映射的值（value）。要把一个消息添加为映射的值，你需要引用一个[未定义的键（key）](#undefined)，这会构造并返回一个新的子消息：

```python
m.message_map[key].submessage_field = 10
```

关于未定义的键的更多信息，请参阅下一节。

#### 引用未定义的键 {#undefined}

在未定义的键方面，Protobuf 映射的语义与 Python `dict` 略有不同。在普通的 Python `dict` 中，引用未定义的键会抛出 KeyError 异常：

```python
>>> x = {}
>>> x[5]
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 5
```

而在 Protobuf 映射中，引用一个未定义的键会在映射中创建该键，其值为零/false/空。这种行为更像 Python 标准库的 `defaultdict`。

```python
>>> dict(m.mapfield)
{}
>>> m.mapfield[5]
0
>>> dict(m.mapfield)
{5: 0}
```

对于以消息类型为值的映射，这种行为尤其方便，因为你可以直接更新所返回消息的字段。

```python
>>> m.message_map[5].foo = 3
```

请注意，即使你没有为消息字段赋任何值，子消息仍会在映射中被创建：

```python
>>> m.message_map[10]
<test_pb2.M2 object at 0x7fb022af28c0>
>>> dict(m.message_map)
{10: <test_pb2.M2 object at 0x7fb022af28c0>}
```

这与普通的[内嵌消息字段](#embedded_message)**不同**：对于后者，只有当你为消息的某个字段赋值后，消息本身才会被创建。

对于阅读你的代码的人来说，像 `m.message_map[10]` 这样单独一条语句可能会创建一个子消息，这一点未必一目了然。因此我们还提供了 `get_or_create()` 方法，它做的事情与前者相同，但其名称更明确地表达了可能创建消息这一点：

```python
# 等价于：
#   m.message_map[10]
# 但更明确地表明这条语句可能会在映射中创建一个新的
# 空消息。
m.message_map.get_or_create(10)
```

### 内存管理 {#clearing-fields}

请注意，清除字段（通过 `ClearField`、`Clear`、`del`（针对列表）或 `ClearExtension`）不一定能回收内存。它只是把对象重置成仿佛一切未设置的样子，但子对象*可能*继续存在。例如，清除一个可重复字段会把它的大小设为 0，但不会放弃其容量（类似于在 C++ 中对 `std::vector` 调用 `.clear()`）。

有多种方法可以确保内存被释放。其中一种方法是在清除字段之后为这个 proto 制作一份副本，因为未使用的内存不会被复制过去：

```python
# 假设 'my_proto' 有一个占用大量内存的字段 'big_field'
# 清除该字段。内存可能仍被保留。
my_proto.ClearField('big_field')

# 复制到新实例。这只会分配必要的内存。
compact_proto = my_proto_pb2.MyProto()
compact_proto.CopyFrom(my_proto)

# 当指向初始 proto 的所有引用都消失后，它会被垃圾回收。
my_proto = compact_proto
```

## 枚举 {#enum}

在 Python 中，枚举就是整数。会为枚举定义的各个取值定义一组整型常量。例如，给定：

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

常量 `VALUE_A`、`VALUE_B` 和 `VALUE_C` 分别以 0、5 和 1234 为值定义。如有需要，你也可以访问 `SomeEnum`。如果枚举定义在外层作用域，这些值就是模块级常量；如果它定义在消息内部（如上例），它们就会成为该消息类的静态成员。

例如，对于 proto 中的以下枚举，你可以通过下面三种方式访问其取值：

```proto
enum SomeEnum {
  VALUE_A = 0;
  VALUE_B = 5;
  VALUE_C = 1234;
}
```

```python
value_a = myproto_pb2.SomeEnum.VALUE_A
# 或者
myproto_pb2.VALUE_A
# 或者
myproto_pb2.SomeEnum.Value('VALUE_A')
```

枚举字段的工作方式与标量字段完全一样。

```python
foo = Foo()
foo.bar = Foo.VALUE_A
assert foo.bar == 0
assert foo.bar == Foo.VALUE_A
```

如果枚举的名称（或某个枚举值）是 Python 关键字，那么它的对象（或该枚举值的属性）将只能通过 `getattr()` 访问，如[与 Python 关键字冲突的名称](#keyword-conflicts)一节所述。

在 proto2 中，枚举是封闭式枚举；在 proto3 中，枚举是开放式枚举。在版次中，`enum_type` 特性（feature）决定枚举的行为。

-   `OPEN` 枚举可以具有任何 `int32` 值，即使该值未在枚举定义中指定。这是版次下的默认行为。
-   `CLOSED` 枚举不能包含枚举类型已定义取值之外的数值。如果你赋的值不在枚举中，生成代码会抛出异常。这等价于 proto2 中枚举的行为。

枚举有许多实用方法，可用于从值获取字段名、从字段名获取值、列出字段等等——这些方法定义在 [`enum_type_wrapper.EnumTypeWrapper`](https://github.com/protocolbuffers/protobuf/blob/master/python/google/protobuf/internal/enum_type_wrapper.py)（生成的枚举类的基类）中。举例来说，如果 `myproto.proto` 中有如下独立枚举：

```proto
enum SomeEnum {
  VALUE_A = 0;
  VALUE_B = 5;
  VALUE_C = 1234;
}
```

……你可以这样做：

```python
self.assertEqual('VALUE_A', myproto_pb2.SomeEnum.Name(myproto_pb2.VALUE_A))
self.assertEqual(5, myproto_pb2.SomeEnum.Value('VALUE_B'))
```

对于声明在协议消息内部的枚举（例如上面的 Foo），语法类似：

```python
self.assertEqual('VALUE_A', myproto_pb2.Foo.SomeEnum.Name(myproto_pb2.Foo.VALUE_A))
self.assertEqual(5, myproto_pb2.Foo.SomeEnum.Value('VALUE_B'))
```

如果多个枚举常量具有相同的值（即别名），则返回最先定义的常量。

```proto
enum SomeEnum {
  option allow_alias = true;
  VALUE_A = 0;
  VALUE_B = 5;
  VALUE_C = 1234;
  VALUE_B_ALIAS = 5;
}
```

在上面的示例中，`myproto_pb2.SomeEnum.Name(5)` 返回 `"VALUE_B"`。

## oneof {#oneof}

给定一个带 oneof 的消息：

```proto
message Foo {
  oneof test_oneof {
     string name = 1;
     int32 serial_number = 2;
  }
}
```

与 `Foo` 对应的 Python 类会拥有名为 `name` 和 `serial_number` 的属性，就像普通的[字段](#fields)一样。但与普通字段不同的是，oneof 中的字段同一时间最多只能设置一个，这由运行时（runtime）保证。例如：

```python
message = Foo()
message.name = "Bender"
assert message.HasField("name")
message.serial_number = 2716057
assert message.HasField("serial_number")
assert not message.HasField("name")
```

消息类还有一个 `WhichOneof` 方法，让你可以查明 oneof 中哪个字段（如果有的话）已被设置。该方法返回已设置字段的名称，如果什么都没有设置则返回 `None`：

```python
assert message.WhichOneof("test_oneof") is None
message.name = "Bender"
assert message.WhichOneof("test_oneof") == "name"
```

除字段名之外，`HasField` 和 `ClearField` 也接受 oneof 名称：

```python
assert not message.HasField("test_oneof")
message.name = "Bender"
assert message.HasField("test_oneof")
message.serial_number = 2716057
assert message.HasField("test_oneof")
message.ClearField("test_oneof")
assert not message.HasField("test_oneof")
assert not message.HasField("serial_number")
```

请注意，对 oneof 调用 `ClearField` 只会清除当前已设置的字段。

## 与 Python 关键字冲突的名称 {#keyword-conflicts}

如果消息、字段、枚举或枚举值的名称是一个 [Python 关键字](https://docs.python.org/3/reference/lexical_analysis#keywords)，那么其对应类或属性的名称保持不变，但你只能使用 Python 的内置函数 [`getattr()`](https://docs.python.org/3/library/functions#getattr) 和 [`setattr()`](https://docs.python.org/3/library/functions#setattr) 来访问它，而不能使用 Python 正常的属性引用语法（即点运算符）。

例如，如果你有如下 `.proto` 定义：

```proto
message Baz {
  optional int32 from = 1
  repeated int32 in = 2;
}
```

你需要像下面这样访问这些字段：

```python
baz = Baz()
setattr(baz, "from", 99)
assert getattr(baz, "from") == 99
getattr(baz, "in").append(42)
assert getattr(baz, "in") == [42]
```

相比之下，如果试图用 `obj.attr` 语法访问这些字段，Python 在解析你的代码时会抛出语法错误：

```python
# 错误！
baz.in  # SyntaxError: invalid syntax（无效语法）
baz.from  # SyntaxError: invalid syntax（无效语法）
```

## 扩展 {#extension}

给定一个带扩展区间（extension range）的 proto2 或版次消息：

```proto
edition = "2023";
message Foo {
  extensions 100 to 199;
}
```

与 `Foo` 对应的 Python 类会有一个名为 `Extensions` 的成员，它是一个字典，将扩展标识符映射到其当前值。

给定如下扩展定义：

```proto
extend Foo {
  int32 bar = 123;
}
```

Protobuf 编译器会生成一个名为 `bar` 的“扩展标识符”。该标识符充当 `Extensions` 字典的键。在该字典中查找值的结果，与你访问同类型的普通字段完全一样。因此，对于上面的示例，你可以这样写：

```python
foo = Foo()
foo.Extensions[proto_file_pb2.bar] = 2
assert foo.Extensions[proto_file_pb2.bar] == 2
```

请注意，你需要指定扩展标识符常量，而不仅仅是字符串名称：这是因为在不同作用域中可能指定多个同名的扩展。

与普通字段类似，`Extensions[...]` 对单数消息返回一个消息对象，对可重复字段返回一个序列。

[`Message`](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message) 接口的 `HasField()` 和 `ClearField()` 方法不能用于扩展；你必须改用 `HasExtension()` 和 `ClearExtension()`。要使用 `HasExtension()` 和 `ClearExtension()` 方法，请传入你要检查其存在性的扩展的 `field_descriptor`。

## 服务 {#service}

如果 `.proto` 文件包含如下一行：

```proto
option py_generic_services = true;
```

那么 Protobuf 编译器将按照本节的描述，基于文件中的服务（service）定义生成代码。但是，生成的代码可能并不理想，因为它不与任何特定的远程过程调用（RPC）系统绑定，因此相比针对单一系统定制的代码需要更多的间接层。如果你*不*希望生成这些代码，请在文件中添加以下行：

```proto
option py_generic_services = false;
```

如果上述两行都未给出，该选项默认为 `false`，因为通用服务已弃用。（注意，在 2.4.0 之前，该选项默认为 `true`。）弃用背后的原因请参见[通用服务的设计决策](/design-decisions/insertion-points-and-generic-services#generic-services)。

基于 `.proto` 语言服务定义的 RPC 系统应当提供[插件（plugin）](/reference/cpp/api-docs/google.protobuf.compiler.plugin.pb)来生成适合该系统的代码。这些插件很可能要求禁用抽象服务，以便它们能够生成自己的同名类。

本节余下部分描述在启用抽象服务时 Protobuf 编译器生成的内容。

### 接口 {#interface}

给定如下服务定义：

```proto
service Foo {
  rpc Bar(FooRequest) returns(FooResponse);
}
```

Protobuf 编译器会生成一个类 `Foo` 来表示此服务。`Foo` 会为服务定义中定义的每个方法提供一个对应的方法。在本例中，方法 `Bar` 的定义如下：

```python
def Bar(self, rpc_controller, request, done)
```

这些参数与 [`Service.CallMethod()`](https://googleapis.dev/python/protobuf/latest/google/protobuf/service.html#google.protobuf.service.Service.CallMethod) 的参数等价，只是 `method_descriptor` 参数是隐含的。

这些生成的方法预期由子类覆写。默认实现只是调用 [`controller.SetFailed()`](https://googleapis.dev/python/protobuf/latest/google/protobuf/service.html#google.protobuf.service.RpcController.SetFailed) 并附上一条说明该方法尚未实现的错误消息，然后调用 `done` 回调。实现你自己的服务时，你必须继承这个生成的服务类，并按需实现其方法。

`Foo` 继承自 `Service` 接口。Protobuf 编译器会按如下方式自动生成 `Service` 各方法的实现：

-   `GetDescriptor`：返回该服务的 [`ServiceDescriptor`](https://googleapis.dev/python/protobuf/latest/google/protobuf/descriptor.html#google.protobuf.descriptor.ServiceDescriptor)。
-   `CallMethod`：根据提供的方法描述符确定正在调用的是哪个方法，并直接调用它。
-   `GetRequestClass` 和 `GetResponseClass`：返回给定方法所对应的正确类型的请求类或响应类。

### 存根 {#stub}

Protobuf 编译器还会为每个服务接口生成一个“存根”（stub）实现，供希望向实现了该服务的服务器发送请求的客户端使用。对于（上文中的）`Foo` 服务，将会定义存根实现 `Foo_Stub`。

`Foo_Stub` 是 `Foo` 的子类。它的构造函数接受一个 [`RpcChannel`](https://googleapis.dev/python/protobuf/latest/google/protobuf/service.html#google.protobuf.service.RpcChannel) 作为参数。存根随后通过调用通道的 `CallMethod()` 方法来实现服务的每个方法。

Protobuf 库本身不包含 RPC 实现。不过，它包含了把生成的服务类接入你所选的任意 RPC 实现所需的全部工具。你只需提供 `RpcChannel` 和 [`RpcController`](https://googleapis.dev/python/protobuf/latest/google/protobuf/service.html#google.protobuf.service.RpcController) 的实现。

## 插件插入点 {#plugins}

希望扩展 Python 代码生成器（code generator）输出的[代码生成器插件](/reference/cpp/api-docs/google.protobuf.compiler.plugin)，可以使用给定的插入点名称插入以下类型的代码。

-   `imports`：导入语句。
-   `module_scope`：顶层声明。

{{% alert title="Warning" color="warning" %}} 不要生成依赖标准代码生成器所声明的私有类成员的代码，因为这些实现细节在 Protobuf 的未来版本中可能会发生变化。 {{% /alert %}}

## 在 Python 与 C++ 之间共享消息 {#sharing-messages}

在 Protobuf Python API 的 4.21.0 版本之前，Python 应用可以通过原生扩展与 C++ 共享消息。从 4.21.0 API 版本开始，默认安装不再支持在 Python 与 C++ 之间共享消息。要在使用 4.x 及更高版本的 Protobuf Python API 时启用这一能力，请定义环境变量 `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=cpp`，并确保已安装 Python/C++ 扩展。
