+++
title = "Protobuf 基础：Python"
weight = 270
linkTitle = "Python"
description = "面向 Python 程序员的 Protobuf 使用基础入门。"
type = "docs"
source_url = "https://protobuf.dev/getting-started/pythontutorial/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本教程为 Python 程序员提供使用 Protobuf 的基础入门，并通过逐步创建一个简单的示例应用，向你展示如何：

-   在 `.proto` 文件中定义消息（message）格式。
-   使用 Protobuf 编译器。
-   使用 Python Protobuf API 写入和读取消息。

本文并不是一份在 Python 中使用 Protobuf 的全面指南。如需更详细的参考信息，请参阅 [Protobuf 语言指南（proto2）](/programming-guides/proto2)、[Protobuf 语言指南（proto3）](/programming-guides/proto3)、[Python API 参考](https://googleapis.dev/python/protobuf/latest/)、[Python 生成代码指南](/reference/python/python-generated)以及[编码参考](/programming-guides/encoding)。

## 问题域 {#problem-domain}

我们要使用的示例是一个非常简单的“通讯录”应用，它可以把人们的联系信息写入文件，也可以从文件中读出。通讯录中的每个人都有姓名、ID、电子邮件地址和联系电话。

如何对这样的结构化数据（structured data）进行序列化（serialization）并读取出来？有以下几种解决办法：

-   使用 Python 的 pickling 机制。由于它内建于语言之中，这是默认的做法，但它对模式（schema）演进的支持并不好；而且如果你需要与用 C++ 或 Java 编写的应用共享数据，它的表现也不太好。
-   你可以自行发明一种临时方式，把各数据项编码进单个字符串——例如把 4 个整数编码成 “12:3:-23:67”。这种方式简单而灵活，但需要专门编写一次性的编码（encoding）与解析（parse）代码，而且解析会带来少量运行时开销。它最适合用于编码非常简单的数据。
-   将数据序列化为 XML。这种方式颇具吸引力，因为 XML（勉强）算是人类可读的，而且许多语言都有绑定库。如果你希望与其他应用/项目共享数据，这可能是个不错的选择。然而，XML 以极度占用空间而著称，对其进行编码/解码可能给应用带来巨大的性能损失。此外，遍历 XML DOM 树通常也比访问类中的简单字段（field）复杂得多。

除了这些方案之外，你还可以使用 Protobuf。Protobuf 正是为解决这一问题而生的灵活、高效、自动化方案。使用 Protobuf 时，你要为想要存储的数据结构编写一份 `.proto` 描述。Protobuf 编译器会据此创建一个类，以高效的二进制格式（binary format）实现 Protobuf 数据的自动编码与解析。生成的类为构成 Protobuf 消息的字段提供 getter 和 setter，并负责把消息作为一个整体进行读写时的各项细节。重要的是，Protobuf 格式支持随时间推移扩展格式，同时代码仍能读取以旧格式编码的数据。

## 在哪里找到示例代码 {#example-code}

示例代码包含在源码包中，位于 “examples” 目录下。[在此下载。](/downloads)

## 定义你的协议格式 {#protocol-format}

要创建你的通讯录应用，需要先从一个 `.proto` 文件开始。`.proto` 文件中的定义很简单：为每个想要序列化的数据结构添加一个*消息*，然后为消息中的每个字段指定名称和类型。下面就是定义你的消息的 `.proto` 文件，即 `addressbook.proto`。

```proto
edition = "2023";

package tutorial;

message Person {
  string name = 1;
  int32 id = 2;
  string email = 3;

  enum PhoneType {
    PHONE_TYPE_UNSPECIFIED = 0;
    PHONE_TYPE_MOBILE = 1;
    PHONE_TYPE_HOME = 2;
    PHONE_TYPE_WORK = 3;
  }

  message PhoneNumber {
    string number = 1;
    PhoneType type = 2 [default = PHONE_TYPE_HOME];
  }

  repeated PhoneNumber phones = 4;
}

message AddressBook {
  repeated Person people = 1;
}
```

可以看到，其语法与 C++ 或 Java 相似。下面我们逐部分过一遍这个文件，看看各部分的作用。

`.proto` 文件以一条 package 声明开头，这有助于避免不同项目之间的命名冲突。在 Python 中，包（package）通常由目录结构决定，因此你在 `.proto` 文件中定义的 `package` 对生成的代码没有影响。不过，你仍然应当声明一个 package，以避免在 Protobuf 命名空间（namespace）以及其他非 Python 语言中发生名称冲突。

接下来是你的消息定义。消息只是一个包含一组带类型字段的聚合体（aggregate）。许多标准简单数据类型都可用作字段类型，包括 `bool`、`int32`、`float`、`double` 和 `string`。你还可以把其他消息类型用作字段类型，为消息添加更深层的结构——在上面的示例中，`Person` 消息包含 `PhoneNumber` 消息，而 `AddressBook` 消息包含 `Person` 消息。你甚至可以把消息类型嵌套定义在其他消息内部——如你所见，`PhoneNumber` 类型就定义在 `Person` 之中。如果希望某个字段的取值限定在一组预定义值之内，你还可以定义枚举（enum）类型——这里的目的是指定电话号码可以是 `PHONE_TYPE_MOBILE`、`PHONE_TYPE_HOME` 或 `PHONE_TYPE_WORK` 这几种电话类型之一。

每个元素上的 “ = 1”、“ = 2” 标记，标识出该字段在二进制编码中使用的唯一“标签”（tag）。字段编号（tag number）1-15 比更大的编号少用一个字节来编码，因此作为一种优化，你可以决定把这些编号用于常用或 repeated 的元素，而把 16 及以上的字段编号留给不那么常用的 optional 元素。repeated 字段中的每个元素都需要重新编码字段编号，因此 repeated 字段特别适合进行这种优化。

关于编写 `.proto` 文件的完整指南——包括所有可能的字段类型——请参阅 [Protobuf 语言指南](/programming-guides/editions)。不过，不要去找类似类继承的机制——Protobuf 并不支持这种做法。

## 编译你的 Protobuf 模式 {#compiling-protocol-buffers}

现在你已经有 `.proto` 文件了，接下来要做的就是生成读写 `AddressBook`（因而也包括 `Person` 和 `PhoneNumber`）消息所需的类。为此，你需要用 Protobuf 编译器 `protoc` 编译你的 `.proto`：

1.  如果尚未安装编译器，请[下载软件包](/downloads)并按照 README 中的说明操作。

2.  现在运行编译器，指定源目录（你的应用源码所在的位置——如果未提供该值，则使用当前目录）、目标目录（希望生成的代码存放的位置；通常与 `$SRC_DIR` 相同），以及你的 `.proto` 的路径。在本例中，应执行以下命令：

    ```shell
    protoc --proto_path=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/addressbook.proto
    ```

    由于你想要的是 Python 类，因此要使用 `--python_out` 选项——其他受支持的语言也提供了类似的选项。

    protoc 还能够通过 `--pyi_out` 生成 Python 存根文件（`.pyi`）。

这会在你指定的目标目录中生成 `addressbook_pb2.py`（或 `addressbook_pb2.pyi`）。

## Protobuf API {#protobuf-api}

与生成 Java 和 C++ Protobuf 代码时不同，Python Protobuf 编译器不会直接为你生成数据访问代码。相反（如果你查看 `addressbook_pb2.py` 就能看到），它会为你的所有消息、枚举和字段生成特殊的描述符（descriptor），外加一些“神秘”的空类——每种消息类型对应一个：

```python
import google3
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.GOOGLE_INTERNAL,
    0,
    20240502,
    0,
    '',
    'main.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()

DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nmain.proto\x12\x08tutorial\"\xa3\x02\n\x06Person\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\x05\x12\r\n\x05\x65mail\x18\x03 \x01(\t\x12,\n\x06phones\x18\x04 \x03(\x0b\x32\x1c.tutorial.Person.PhoneNumber\x1aX\n\x0bPhoneNumber\x12\x0e\n\x06number\x18\x01 \x01(\t\x12\x39\n\x04type\x18\x02 \x01(\x0e\x32\x1a.tutorial.Person.PhoneType:\x0fPHONE_TYPE_HOME\"h\n\tPhoneType\x12\x1a\n\x16PHONE_TYPE_UNSPECIFIED\x10\x00\x12\x15\n\x11PHONE_TYPE_MOBILE\x10\x01\x12\x13\n\x0fPHONE_TYPE_HOME\x10\x02\x12\x13\n\x0fPHONE_TYPE_WORK\x10\x03\"/\n\x0b\x41\x64\x64ressBook\x12 \n\x06people\x18\x01 \x03(\x0b\x32\x10.tutorial.Person')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'google3.main_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_PERSON']._serialized_start=25
  _globals['_PERSON']._serialized_end=316
  _globals['_PERSON_PHONENUMBER']._serialized_start=122
  _globals['_PERSON_PHONENUMBER']._serialized_end=210
  _globals['_PERSON_PHONETYPE']._serialized_start=212
  _globals['_PERSON_PHONETYPE']._serialized_end=316
  _globals['_ADDRESSBOOK']._serialized_start=318
  _globals['_ADDRESSBOOK']._serialized_end=365
# @@protoc_insertion_point(module_scope)
```

每个类中关键的一行是 `__metaclass__ = reflection.GeneratedProtocolMessageType`。Python 元类（metaclass）的工作细节超出了本教程的范围，但你可以把它们想象成创建类时使用的模板。在加载时，`GeneratedProtocolMessageType` 元类会利用指定的描述符，创建你操作每种消息类型所需的全部 Python 方法，并把它们添加到相应的类上。此后，你就可以在代码中使用这些补全完毕的类了。

这一切的最终效果是：你可以使用 `Person` 类，就好像它把 `Message` 基类的每个字段都定义成了普通字段一样。例如，你可以这样写：

```python
import addressbook_pb2
person = addressbook_pb2.Person()
person.id = 1234
person.name = "John Doe"
person.email = "jdoe@example.com"
phone = person.phones.add()
phone.number = "555-4321"
phone.type = addressbook_pb2.Person.PHONE_TYPE_HOME
```

请注意，这些赋值并不只是给一个普通的 Python 对象随意添加新字段。如果你试图给 `.proto` 文件中未定义的字段赋值，就会抛出 `AttributeError`。如果给字段赋了类型不匹配的值，则会抛出 `TypeError`。另外，在字段尚未设置时读取它的值，会返回默认值（default value）。

```python
person.no_such_field = 1  # 抛出 AttributeError
person.id = "1234"        # 抛出 TypeError
```

关于协议编译器针对任何特定字段定义究竟会生成哪些成员的详细信息，请参阅 [Python 生成代码参考](/reference/python/python-generated)。

### 枚举 {#enums}

枚举会被元类展开为一组带整数值的符号常量。因此举例来说，常量 `addressbook_pb2.Person.PhoneType.PHONE_TYPE_WORK` 的值为 2。

### 标准消息方法 {#standard-message-methods}

每个消息类还包含许多其他方法，让你能够检查或操作整个消息，包括：

-   `IsInitialized()`：检查是否所有 required 字段都已设置。
-   `__str__()`：返回消息的人类可读表示形式，对调试特别有用。（通常通过 `str(message)` 或 `print message` 调用。）
-   `CopyFrom(other_msg)`：用给定消息的值覆盖当前消息。
-   `Clear()`：把所有元素清空回空状态。

这些方法实现了 `Message` 接口。更多信息请参阅 [`Message` 的完整 API 文档](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message)。

### 解析与序列化 {#parsing-serialization}

最后，每个 Protobuf 类都有一些方法，用于通过 Protobuf [二进制格式](/programming-guides/encoding)写入和读取你所选类型的消息。这些方法包括：

-   `SerializeToString()`：序列化该消息并把它作为字符串返回。注意，这些字节是二进制的，不是文本；我们只是把 `str` 类型当作一个方便的容器来使用。
-   `ParseFromString(data)`：从给定的字符串解析出一条消息。

这些只是用于解析和序列化的众多选项中的一小部分。同样，完整列表请参阅 [`Message` API 参考](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message)。

你还可以轻松地把消息序列化为 JSON 以及从 JSON 反序列化回来。`json_format` 模块为此提供了辅助方法：

-   `MessageToJson(message)`：把消息序列化为 JSON 字符串。
-   `Parse(json_string, message)`：把 JSON 字符串解析进给定的消息。

例如：

```python
from google.protobuf import json_format
import addressbook_pb2

person = addressbook_pb2.Person()
person.id = 1234
person.name = "John Doe"
person.email = "jdoe@example.com"

# 序列化为 JSON
json_string = json_format.MessageToJson(person)

# 从 JSON 解析
new_person = addressbook_pb2.Person()
json_format.Parse(json_string, new_person)
```

{{% alert title="Important" color="warning" %}} **Protobuf 与面向对象设计**
Protobuf 类基本上只是数据载体（类似于 C 语言中的 struct），并不提供额外的功能；在对象模型中，它们并不适合作为一等公民。如果你想为生成的类添加更丰富的行为，最好的做法是把生成的 Protobuf 类包装在一个应用特定的类中。如果你无法控制 `.proto` 文件的设计（例如你在复用另一个项目的文件），把 Protobuf 消息包装起来也是个好主意。在这种情况下，你可以利用包装类来打造一个更适合你的应用独特环境的接口：隐藏部分数据和方法、暴露便捷函数等等。**你绝不应该通过继承生成的类来为其添加行为**。这样做会破坏内部机制，而且本来也不符合良好的面向对象实践。 {{% /alert %}}

## 写入消息 {#writing-a-message}

现在我们来试用你的 Protobuf 类。你希望通讯录应用实现的第一件事，就是把个人信息写入通讯录文件。为此，你需要创建并填充 Protobuf 类的实例，然后把它们写入输出流。

下面这个程序会从文件中读取 `AddressBook`，根据用户输入向其中添加一个新的 `Person`，然后把新的 `AddressBook` 重新写回文件。其中直接调用或引用协议编译器所生成代码的部分已突出显示。

```python
#!/usr/bin/env python3

import addressbook_pb2
import sys

# 此函数根据用户输入填充一条 Person 消息。
def PromptForAddress(person):
  person.id = int(input("Enter person ID number: "))
  person.name = input("Enter name: ")

  email = input("Enter email address (blank for none): ")
  if email != "":
    person.email = email

  while True:
    number = input("Enter a phone number (or leave blank to finish): ")
    if number == "":
      break

    phone_number = person.phones.add()
    phone_number.number = number

    phone_type = input("Is this a mobile, home, or work phone? ")
    if phone_type == "mobile":
      phone_number.type = addressbook_pb2.Person.PhoneType.PHONE_TYPE_MOBILE
    elif phone_type == "home":
      phone_number.type = addressbook_pb2.Person.PhoneType.PHONE_TYPE_HOME
    elif phone_type == "work":
      phone_number.type = addressbook_pb2.Person.PhoneType.PHONE_TYPE_WORK
    else:
      print("Unknown phone type; leaving as default value.")

# 主过程：从文件中读取整个通讯录，
#   根据用户输入添加一个人，然后把结果写回
#   同一个文件。
if len(sys.argv) != 2:
  print("Usage:", sys.argv[0], "ADDRESS_BOOK_FILE")
  sys.exit(-1)

address_book = addressbook_pb2.AddressBook()

# 读取现有的通讯录。
try:
  with open(sys.argv[1], "rb") as f:
    address_book.ParseFromString(f.read())
except IOError:
  print(sys.argv[1] + ": Could not open file.  Creating a new one.")

# 添加一条地址。
PromptForAddress(address_book.people.add())

# 把新的通讯录写回磁盘。
with open(sys.argv[1], "wb") as f:
  f.write(address_book.SerializeToString())
```

## 读取消息 {#reading-a-message}

当然，如果无法从中取出任何信息，通讯录就没多大用处了！本示例读取由上一个示例创建的文件，并打印其中的所有信息。

```python
#!/usr/bin/env python3

import addressbook_pb2
import sys

# 遍历 AddressBook 中的所有人并打印他们的信息。
def ListPeople(address_book):
  for person in address_book.people:
    print("Person ID:", person.id)
    print("  Name:", person.name)
    if person.HasField('email'):
      print("  E-mail address:", person.email)

    for phone_number in person.phones:
      if phone_number.type == addressbook_pb2.Person.PhoneType.PHONE_TYPE_MOBILE:
        print("  Mobile phone #: ", end="")
      elif phone_number.type == addressbook_pb2.Person.PhoneType.PHONE_TYPE_HOME:
        print("  Home phone #: ", end="")
      elif phone_number.type == addressbook_pb2.Person.PhoneType.PHONE_TYPE_WORK:
        print("  Work phone #: ", end="")
      print(phone_number.number)

# 主过程：从文件中读取整个通讯录，并打印其中的
#   全部信息。
if len(sys.argv) != 2:
  print("Usage:", sys.argv[0], "ADDRESS_BOOK_FILE")
  sys.exit(-1)

address_book = addressbook_pb2.AddressBook()

# 读取现有的通讯录。
with open(sys.argv[1], "rb") as f:
  address_book.ParseFromString(f.read())

ListPeople(address_book)
```

## 扩展 Protobuf 消息 {#extending-a-protobuf}

在你发布（release）使用 Protobuf 消息的代码之后，你无疑会想“改进”消息的定义。如果你希望新消息向后兼容（backwards-compatible）、旧消息向前兼容（forward-compatible）——你几乎肯定希望如此——那么就需要遵守一些规则。在消息的新版本中：

-   你*不得*更改任何现有字段的字段编号。
-   你*不得*添加或删除任何 required 字段。
-   你*可以*删除 optional 字段或 repeated 字段。
-   你*可以*添加新的 optional 字段或 repeated 字段，但必须使用全新的字段编号（也就是说，这些编号在此消息中从未被使用过，连已删除字段用过的也不行）。

（这些规则有[一些例外](/programming-guides/proto2#updating)，但极少使用。）

只要遵守这些规则，旧代码就能顺利读取新消息，并直接忽略任何新字段。对旧代码而言，被删除的 optional 字段只会呈现其默认值，被删除的 repeated 字段则为空。新代码也能透明地读取旧消息。不过请记住，新增的 optional 字段不会出现在旧消息中，因此你要么用 `HasField('field_name')` 显式检查字段是否已设置，要么在 `.proto` 文件中、于字段编号之后用 `[default = value]` 提供一个合理的默认值。如果没有为 optional 元素指定默认值，就会使用类型相关的默认值：字符串的默认值是空字符串，布尔类型的默认值是 false，数值类型的默认值是 0。另外还要注意，如果你新增了一个 repeated 字段，你的新代码将无法分辨该字段是被（新代码）留空，还是（被旧代码）从未设置过，因为对它没有 `HasField` 检查。

## 高级用法 {#advanced-usage}

Protobuf 的用途远不止简单的访问器（accessor）和序列化。请务必浏览 [Python API 参考](https://googleapis.dev/python/protobuf/latest/)，看看你还能用它做什么。

协议消息类提供的一个关键特性是*反射（reflection）*。你可以在不针对任何特定消息类型编写代码的情况下，遍历消息的字段并操作它们的值。反射的一个非常有用的用途，是在协议消息与其他编码之间进行相互转换，例如 XML 或 JSON（示例参见[解析与序列化](#parsing-serialization)）。反射更高级的用法，可能是找出两个同类型消息之间的差异，或者开发某种“协议消息正则表达式”，让你可以编写表达式来匹配特定的消息内容。只要发挥想象力，你就能把 Protobuf 应用到比最初预期广泛得多的问题上！

反射由 [`Message` 接口](https://googleapis.dev/python/protobuf/latest/google/protobuf/message.html#google.protobuf.message.Message)提供。
