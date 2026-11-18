+++
title = "Protobuf 基础：C#"
weight = 220
linkTitle = "C#"
description = "面向 C# 程序员的 Protobuf 使用基础入门。"
type = "docs"
source_url = "https://protobuf.dev/getting-started/csharptutorial/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

本教程（tutorial）为 C# 程序员提供使用 Protobuf 的基础入门，采用的是 Protobuf 语言的 [proto3](/programming-guides/proto3) 版本（version）。通过逐步创建一个简单的示例应用，它将向你展示如何：

-   在 `.proto` 文件中定义消息（message）格式。
-   使用 Protobuf 编译器。
-   使用 C# Protobuf API 写入和读取消息。

本文并不是一份在 C# 中使用 Protobuf 的全面指南。如需更详细的参考信息，请参阅 [Protobuf 语言指南](/programming-guides/proto3)、[C# API 参考](/reference/csharp/api-docs)、[C# 生成代码指南](/reference/csharp/csharp-generated)以及[编码参考](/programming-guides/encoding)。

## 问题域 {#problem-domain}

我们要使用的示例是一个非常简单的“通讯录”应用，它可以把人们的联系信息写入文件，也可以从文件中读出。通讯录中的每个人都有姓名、ID、电子邮件地址和联系电话。

如何序列化（serialization）这样的结构化数据（structured data）并把它们读取出来？有以下几种解决办法：

-   使用 .NET 二进制序列化，即 `System.Runtime.Serialization.Formatters.Binary.BinaryFormatter` 及相关类。这种做法在面对变更时非常脆弱，某些情况下数据体积的开销也很大；此外，如果需要与为其他平台编写的应用共享数据，它的表现也不太好。
-   你可以自行发明一种临时方案，把各个数据项编码到单个字符串中——比如把 4 个整数编码成 “12:3:-23:67”。这种做法简单而灵活，但需要专门编写一次性的编码与解析（parse）代码，而且解析会带来少量运行时（runtime）开销。它最适合用于编码非常简单的数据。
-   将数据序列化为 XML。这种方式颇具吸引力，因为 XML（勉强）算是人类可读的，而且许多语言都有绑定库。如果你希望与其他应用/项目共享数据，这可能是个不错的选择。然而，XML 以极度占用空间而著称，对其进行编码/解码可能给应用带来巨大的性能损失。此外，遍历 XML DOM 树通常也比访问类中的简单字段（field）复杂得多。

Protobuf 正是为解决这一问题而生的灵活、高效、自动化方案。使用 Protobuf 时，你要为想要存储的数据结构编写一份 `.proto` 描述。Protobuf 编译器会据此创建一个类，以高效的二进制格式（binary format）实现 Protobuf 数据的自动编码（encoding）与解析。生成的类为构成 Protobuf 消息的字段提供 getter 和 setter，并负责将消息作为一个整体进行读写时的各项细节。重要的是，Protobuf 格式支持随时间推移扩展格式，同时代码仍能读取以旧格式编码的数据。

## 在哪里找到示例代码 {#example-code}

我们的示例是一个命令行应用，用于管理采用 Protobuf 编码的通讯录数据文件。`AddressBook` 命令（参见：[Program.cs](//github.com/protocolbuffers/protobuf/blob/master/csharp/src/AddressBook/Program.cs)）可以向数据文件添加新条目，也可以解析数据文件并把数据打印到控制台。

你可以在 GitHub 仓库的 [examples 目录](https://github.com/protocolbuffers/protobuf/tree/master/examples)和 [`csharp/src/AddressBook` 目录](https://github.com/protocolbuffers/protobuf/tree/master/csharp/src/AddressBook)中找到完整示例。

## 定义你的协议格式 {#protocol-format}

要创建通讯录应用，需要先从一个 `.proto` 文件开始。`.proto` 文件中的定义很简单：为你想要序列化的每个数据结构添加一个*消息*，然后为消息中的每个字段指定名称和类型。在我们的示例中，定义这些消息的 `.proto` 文件是 [`addressbook.proto`](https://github.com/protocolbuffers/protobuf/blob/master/examples/addressbook.proto)。

`.proto` 文件以 package 声明开头，这有助于避免不同项目之间的命名冲突。

```proto
syntax = "proto3";
package tutorial;

import "google/protobuf/timestamp.proto";
```

在 C# 中，如果未指定 `csharp_namespace`，生成的类将被放置在与 `package` 名称一致的命名空间（namespace）中。在我们的示例中，指定了 `csharp_namespace` 选项来覆盖默认值，因此生成代码（generated code）使用 `Google.Protobuf.Examples.AddressBook` 而非 `Tutorial` 作为命名空间。

```csharp
option csharp_namespace = "Google.Protobuf.Examples.AddressBook";
```

接下来是消息定义。消息只是一个包含一组带类型字段的聚合体（aggregate）。许多标准简单数据类型都可用作字段类型，包括 `bool`、`int32`、`float`、`double` 和 `string`。你还可以把其他消息类型用作字段类型，为消息添加更深的结构。

```proto
message Person {
  string name = 1;
  int32 id = 2;  // 此人的唯一 ID 编号。
  string email = 3;

  enum PhoneType {
    PHONE_TYPE_UNSPECIFIED = 0;
    PHONE_TYPE_MOBILE = 1;
    PHONE_TYPE_HOME = 2;
    PHONE_TYPE_WORK = 3;
  }

  message PhoneNumber {
    string number = 1;
    PhoneType type = 2;
  }

  repeated PhoneNumber phones = 4;

  google.protobuf.Timestamp last_updated = 5;
}

// 我们的通讯录文件就是一条这样的消息。
message AddressBook {
  repeated Person people = 1;
}
```

在上面的示例中，`Person` 消息包含 `PhoneNumber` 消息，而 `AddressBook` 消息包含 `Person` 消息。你甚至可以在其他消息内部定义嵌套类型（nested type）的消息——正如你所见，`PhoneNumber` 类型就定义在 `Person` 内部。如果希望某个字段的取值限定在一组预定义值之内，你还可以定义枚举（`enum`）类型——这里你要指定的是电话号码只能是 `PHONE_TYPE_MOBILE`、`PHONE_TYPE_HOME` 或 `PHONE_TYPE_WORK` 之一。

每个元素上的“ = 1”、“ = 2”标记，标识着该字段在二进制编码中使用的唯一“标签（tag）”。标签编号 1-15 比更大的编号在编码时少占一个字节，因此作为一种优化，你可以决定把 1-15 这些标签用于常用或可重复（repeated）的元素，而把 16 及以上的标签留给不那么常用的 optional 元素。repeated 字段中的每个元素都需要重新编码标签编号，因此 repeated 字段尤其适合应用这种优化。

如果字段值未被设置，就会使用[默认值](/programming-guides/proto3#default)：数值类型为零，字符串类型为空字符串，布尔类型为 false。对于内嵌消息，默认值始终是该消息的“默认实例”（default instance）或“原型”（prototype），即一个所有字段都未设置的消息实例。调用访问器（accessor）获取某个未显式设置的字段的值时，返回的总是该字段的默认值。

如果字段被声明为 `repeated`，该字段就可以重复任意多次（包括零次）。重复值在 Protobuf 消息中的顺序会得到保留。可以把 repeated 字段看作大小可动态变化的数组。

关于编写 `.proto` 文件的完整指南——包括所有可能的字段类型——请参阅 [Protobuf 语言指南](/programming-guides/proto3)。不过，不要指望找到类似类继承的机制——Protobuf 不支持这种做法。

## 编译你的 Protobuf 模式（schema）{#compiling-protocol-buffers}

现在你已经有 `.proto` 文件了，接下来要做的就是生成读写 `AddressBook`（进而包括 `Person` 和 `PhoneNumber`）消息所需的类。为此，你需要用 Protobuf 编译器 `protoc` 编译你的 `.proto` 文件：

1.  如果尚未安装编译器，请[下载安装包](/downloads)，并按照 README 中的说明操作。

2.  现在运行编译器，指定源目录（应用源代码所在的目录——如果不提供该值，则使用当前目录）、目标目录（生成代码的存放位置；通常与 `$SRC_DIR` 相同）以及 `.proto` 文件的路径。在本例中，应执行以下命令：

    ```shell
    protoc -I=$SRC_DIR --csharp_out=$DST_DIR $SRC_DIR/addressbook.proto
    ```

    由于你需要的是 C# 代码，因此要使用 `--csharp_out` 选项——其他受支持的语言也提供了类似的选项。

这会在你指定的目标目录中生成 `Addressbook.cs`。要编译这段代码，你需要一个引用了 `Google.Protobuf` 程序集（assembly）的项目。

## Addressbook 类 {#addressbook-classes}

生成 `Addressbook.cs` 会得到 5 个有用的类型：

-   一个静态 `Addressbook` 类，包含 Protobuf 消息的元数据。
-   一个 `AddressBook` 类，带有只读的 `People` 属性。
-   一个 `Person` 类，具有 `Name`、`Id`、`Email` 和 `Phones` 属性。
-   一个 `PhoneNumber` 类，嵌套在静态 `Person.Types` 类中。
-   一个 `PhoneType` 枚举，同样嵌套在 `Person.Types` 中。

关于究竟生成了哪些内容，你可以在 [C# 生成代码指南](/reference/csharp/csharp-generated)中读到更多细节；但在大多数情况下，你完全可以把它们当作再普通不过的 C# 类型来使用。需要特别指出的一点是：所有对应 repeated 字段的属性都是只读的。你可以向该集合添加元素或从中移除元素，但不能用一个完全独立的集合替换它。repeated 字段的集合类型始终是 `RepeatedField<T>`。该类型类似于 `List<T>`，但额外提供了几个便利方法，例如接受元素集合的 `Add` 重载，便于在集合初始化器（collection initializer）中使用。

下面示例演示了如何创建一个 Person 实例：

```csharp
Person john = new Person
{
    Id = 1234,
    Name = "John Doe",
    Email = "jdoe@example.com",
    Phones = { new Person.Types.PhoneNumber { Number = "555-4321", Type = Person.Types.PhoneType.Home } }
};
```

注意，借助 C# 6 的 `using static`，你可以消除 `Person.Types` 这种繁琐的写法：

```csharp
// 将这行加到其他 using 指令中
using static Google.Protobuf.Examples.AddressBook.Person.Types;
...
// 前面对 Phones 的赋值现在可以简化为：
Phones = { new PhoneNumber { Number = "555-4321", Type = PhoneType.HOME } }
```

## 解析与序列化 {#parsing-serialization}

使用 Protobuf 的全部意义就在于把你的数据序列化，以便在其他地方解析。每个生成的类都有一个 `WriteTo(CodedOutputStream)` 方法，其中 `CodedOutputStream` 是 Protobuf 运行时库中的一个类。不过，通常你会使用某个扩展（extension）方法把消息写入常规的 `System.IO.Stream`，或者把消息转换为字节数组或 `ByteString`。这些扩展方法位于 `Google.Protobuf.MessageExtensions` 类中，因此当你想进行序列化时，通常需要为 `Google.Protobuf` 命名空间添加一条 `using` 指令。例如：

```csharp
using Google.Protobuf;
...
Person john = ...; // 代码同前
using (var output = File.Create("john.dat"))
{
    john.WriteTo(output);
}
```

解析同样简单。每个生成的类都有一个静态 `Parser` 属性，它会返回该类型的 `MessageParser<T>`。`MessageParser<T>` 进而提供了用于解析流、字节数组和 `ByteString` 的方法。要解析我们刚创建的文件，可以使用：

```csharp
Person john;
using (var input = File.OpenRead("john.dat"))
{
    john = Person.Parser.ParseFrom(input);
}
```

一个使用这些消息来维护通讯录（添加新条目、列出已有条目）的完整示例程序可在 [GitHub 仓库](https://github.com/protocolbuffers/protobuf/tree/master/csharp/src/AddressBook)中找到。

## 扩展 Protobuf 消息 {#extending-a-protobuf}

在你发布（release）使用 Protobuf 消息的代码之后，你迟早会想“改进”消息的定义。如果你希望新消息向后兼容（backwards-compatible）、旧消息向前兼容（forward-compatible）——你几乎肯定希望如此——那么需要遵守一些规则。在消息的新版本中：

-   你*不得*更改任何现有字段的标签编号。
-   你*可以*删除字段。
-   你*可以*添加新字段，但必须使用全新的标签编号（即此消息中从未使用过的编号，连已删除字段用过的也不行）。

（这些规则有[一些例外](/programming-guides/proto3#updating)，但极少用到。）

只要遵守这些规则，旧代码就能顺利读取新消息，并直接忽略所有新字段。对旧代码而言，被删除的非重复（singular）字段只会呈现其默认值，被删除的 repeated 字段则为空。新代码也能透明地读取旧消息。

不过请记住，旧消息中不会出现新字段，因此你需要围绕默认值做出合理的处理。不同类型使用各自特定的[默认值](/programming-guides/proto3#default)：字符串类型的默认值是空字符串，布尔类型的默认值是 false，数值类型的默认值是零。

## 反射 {#reflection}

消息描述符（descriptor）——即 `.proto` 文件中的信息——与消息实例都可以通过反射（reflection）API 以编程方式进行检查。在编写通用代码时（比如实现另一种文本格式（text format）或一个智能 diff 工具），这会很有用。每个生成的类都有一个静态 `Descriptor` 属性，而任何实例的描述符都可以通过 `IMessage.Descriptor` 属性获取。作为一个简单的用法示例，下面是一个打印任意消息顶层字段的简短方法。

```csharp
public void PrintMessage(IMessage message)
{
    var descriptor = message.Descriptor;
    foreach (var field in descriptor.Fields.InDeclarationOrder())
    {
        Console.WriteLine(
            "Field {0} ({1}): {2}",
            field.FieldNumber,
            field.Name,
            field.Accessor.GetValue(message);
    }
}
```
