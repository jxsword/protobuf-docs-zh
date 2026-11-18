+++
title = "Protobuf 基础：Dart"
weight = 230
linkTitle = "Dart"
description = "面向 Dart 程序员的 Protobuf 使用基础入门。"
type = "docs"
source_url = "https://protobuf.dev/getting-started/darttutorial/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

本教程为 Dart 程序员提供使用 Protobuf 的基础入门，使用 Protobuf 语言的 [proto3](/programming-guides/proto3) 版本，并通过逐步创建一个简单的示例应用，向你展示如何：

-   在 `.proto` 文件中定义消息（message）格式。
-   使用 Protobuf 编译器。
-   使用 Dart Protobuf API 写入和读取消息。

本文并不是一份在 Dart 中使用 Protobuf 的全面指南。如需更详细的参考信息，请参阅 [Protobuf 语言指南](/programming-guides/proto3)、[Dart 语言之旅](https://www.dartlang.org/guides/language/language-tour)、[Dart API 参考](https://pub.dartlang.org/documentation/protobuf)、[Dart 生成代码指南](/reference/dart/dart-generated)以及[编码参考](/programming-guides/encoding)。

## 问题域 {#problem-domain}

我们要使用的示例是一个非常简单的“通讯录”应用，它可以把人们的联系信息写入文件，也可以从文件中读出。通讯录中的每个人都有姓名、ID、电子邮件地址和联系电话。

如何对这样的结构化数据（structured data）进行序列化（serialization）并读取出来？有以下几种解决办法：

-   你可以自行发明一种临时方式，把各数据项编码进单个字符串——例如把 4 个整数编码成 “12:3:-23:67”。这种方式简单而灵活，但需要专门编写一次性的编码（encoding）与解析（parse）代码，而且解析会带来少量运行时开销。它最适合用于编码非常简单的数据。
-   将数据序列化为 XML。这种方式颇具吸引力，因为 XML（勉强）算是人类可读的，而且许多语言都有绑定库。如果你希望与其他应用/项目共享数据，这可能是个不错的选择。然而，XML 以极度占用空间而著称，对其进行编码/解码可能给应用带来巨大的性能损失。此外，遍历 XML DOM 树通常也比访问类中的简单字段（field）复杂得多。

Protobuf 正是为解决这一问题而生的灵活、高效、自动化方案。使用 Protobuf 时，你要为想要存储的数据结构编写一份 `.proto` 描述。Protobuf 编译器会据此创建一个类，以高效的二进制格式（binary format）实现 Protobuf 数据的自动编码与解析。生成的类为构成 Protobuf 消息的字段提供 getter 和 setter，并负责把消息作为一个整体进行读写时的各项细节。重要的是，Protobuf 格式支持随时间推移扩展格式，同时代码仍能读取以旧格式编码的数据。

## 在哪里找到示例代码 {#example-code}

我们的示例是一组用于管理通讯录数据文件的命令行应用，该数据文件使用 Protobuf 编码。命令 `dart add_person.dart` 用于向数据文件添加一条新记录。命令 `dart list_people.dart` 用于解析数据文件并把数据打印到控制台。

你可以在 GitHub 仓库的 [examples 目录](https://github.com/protocolbuffers/protobuf/tree/master/examples)中找到完整示例。

## 定义你的协议格式 {#protocol-format}

要创建你的通讯录应用，需要先从一个 `.proto` 文件开始。`.proto` 文件中的定义很简单：为每个想要序列化的数据结构添加一个*消息*，然后为消息中的每个字段指定名称和类型。在我们的示例中，定义这些消息的 `.proto` 文件是 [`addressbook.proto`](https://github.com/protocolbuffers/protobuf/blob/master/examples/addressbook.proto)。

`.proto` 文件以一条 package 声明开头，这有助于避免不同项目之间的命名冲突。

```proto
syntax = "proto3";
package tutorial;

import "google/protobuf/timestamp.proto";
```

接下来是消息定义。消息只是一个包含一组带类型字段的聚合体（aggregate）。许多标准简单数据类型都可用作字段类型，包括 `bool`、`int32`、`float`、`double` 和 `string`。你还可以把其他消息类型用作字段类型，为消息添加更深层的结构。

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

// 我们的通讯录文件其实就是一条这样的消息。
message AddressBook {
  repeated Person people = 1;
}
```

在上面的示例中，`Person` 消息包含 `PhoneNumber` 消息，而 `AddressBook` 消息包含 `Person` 消息。你甚至可以把消息类型嵌套定义在其他消息内部——如你所见，`PhoneNumber` 类型就定义在 `Person` 之中。如果希望某个字段的取值限定在一组预定义值之内，你还可以定义 `enum` 枚举类型——这里是要指定电话号码可以是 `PHONE_TYPE_MOBILE`、`PHONE_TYPE_HOME` 或 `PHONE_TYPE_WORK` 之一。

每个元素上的 “ = 1”、“ = 2” 标记，标识出该字段在二进制编码中使用的唯一“标签（tag）”。字段编号 1-15 比更大的编号少用一个字节来编码，因此作为一种优化，你可以决定把 1-15 这些编号用于常用或可重复（repeated）的元素，而把 16 及以上的字段编号留给不那么常用的可选（optional）元素。repeated 字段中的每个元素都需要重新编码字段编号，因此 repeated 字段尤其适合采用这种优化。

如果字段值未设置，就会使用[默认值（default value）](/programming-guides/proto3#default)：数值类型为 0，字符串为空字符串，布尔类型为 false。对于内嵌的消息，默认值始终是该消息的“默认实例”或“原型”，即所有字段都未设置的那个实例。调用访问器（accessor）获取某个未显式设置的字段的值时，总会返回该字段的默认值。

如果某个字段是 `repeated`，那么该字段可以重复任意多次（包括零次）。重复值在 Protobuf 消息中的顺序会得到保留。可以把 repeated 字段看作大小动态可变的数组。

关于编写 `.proto` 文件的完整指南——包括所有可能的字段类型——请参阅 [Protobuf 语言指南](/programming-guides/proto3)。不过，不要去找类似类继承的机制——Protobuf 并不支持这种做法。

## 编译你的 Protobuf 模式（schema）{#compiling-protocol-buffers}

现在你已经有 `.proto` 文件了，接下来要做的就是生成读写 `AddressBook`（因而也包括 `Person` 和 `PhoneNumber`）消息所需的类。为此，你需要用 Protobuf 编译器 `protoc` 编译你的 `.proto`：

1.  如果尚未安装编译器，请[下载安装包](/downloads)并按照 README 中的说明操作。

2.  按照[其 README](https://github.com/google/protobuf.dart/tree/master/protoc_plugin#how-to-build) 中的说明安装 Dart Protobuf 插件（plugin）。可执行文件 `bin/protoc-gen-dart` 必须位于你的 `PATH` 中，Protobuf 编译器 `protoc` 才能找到它。

3.  现在运行编译器，指定源目录（你的应用源码所在的位置——如果未提供该值，则使用当前目录）、目标目录（希望生成的代码存放的位置；通常与 `$SRC_DIR` 相同），以及你的 `.proto` 的路径。在本例中，应执行以下命令：

    ```shell
    protoc -I=$SRC_DIR --dart_out=$DST_DIR $SRC_DIR/addressbook.proto
    ```

    由于你想要的是 Dart 代码，因此要使用 `--dart_out` 选项——其他受支持的语言也提供了类似的选项。

这会在你指定的目标目录中生成 `addressbook.pb.dart`。

## Protobuf API {#protobuf-api}

生成 `addressbook.pb.dart` 会为你提供以下有用的类型：

-   一个 `AddressBook` 类，带有 `List<Person> get people` getter。
-   一个 `Person` 类，带有针对 `name`、`id`、`email` 和 `phones` 的访问器方法。
-   一个 `Person_PhoneNumber` 类，带有针对 `number` 和 `type` 的访问器方法。
-   一个 `Person_PhoneType` 类，为 `Person.PhoneType` 枚举中的每个值提供静态字段。

如需进一步了解究竟生成了哪些内容，请参阅 [Dart 生成代码指南](/reference/dart/dart-generated)。

## 写入消息 {#writing-a-message}

现在我们来试用你的 Protobuf 类。你希望通讯录应用实现的第一件事，就是把个人信息写入通讯录文件。为此，你需要创建并填充 Protobuf 类的实例，然后把它们写入输出流。

下面这个程序会从文件中读取 `AddressBook`，根据用户输入向其中添加一个新的 `Person`，然后把新的 `AddressBook` 重新写回文件。其中直接调用或引用协议编译器所生成代码的部分已突出显示。

```dart
import 'dart:io';

import 'dart_tutorial/addressbook.pb.dart';

// 此函数根据用户输入填充一条 Person 消息。
Person promptForAddress() {
  Person person = Person();

  print('Enter person ID: ');
  String input = stdin.readLineSync();
  person.id = int.parse(input);

  print('Enter name');
  person.name = stdin.readLineSync();

  print('Enter email address (blank for none) : ');
  String email = stdin.readLineSync();
  if (email.isNotEmpty) {
    person.email = email;
  }

  while (true) {
    print('Enter a phone number (or leave blank to finish): ');
    String number = stdin.readLineSync();
    if (number.isEmpty) break;

    Person_PhoneNumber phoneNumber = Person_PhoneNumber();

    phoneNumber.number = number;
    print('Is this a mobile, home, or work phone? ');

    String type = stdin.readLineSync();
    switch (type) {
      case 'mobile':
        phoneNumber.type = Person_PhoneType.PHONE_TYPE_MOBILE;
        break;
      case 'home':
        phoneNumber.type = Person_PhoneType.PHONE_TYPE_HOME;
        break;
      case 'work':
        phoneNumber.type = Person_PhoneType.PHONE_TYPE_WORK;
        break;
      default:
        print('Unknown phone type.  Using default.');
    }
    person.phones.add(phoneNumber);
  }

  return person;
}

// 从文件中读取整个通讯录，
// 根据用户输入添加一个人，然后把结果写回同一个文件。
main(List arguments) {
  if (arguments.length != 1) {
    print('Usage: add_person ADDRESS_BOOK_FILE');
    exit(-1);
  }

  File file = File(arguments.first);
  AddressBook addressBook;
  if (!file.existsSync()) {
    print('File not found. Creating new file.');
    addressBook = AddressBook();
  } else {
    addressBook = AddressBook.fromBuffer(file.readAsBytesSync());
  }
  addressBook.people.add(promptForAddress());
  file.writeAsBytes(addressBook.writeToBuffer());
}
```

## 读取消息 {#reading-a-message}

当然，如果无法从中取出任何信息，通讯录就没多大用处了！本示例读取由上一个示例创建的文件，并打印其中的所有信息。

```dart
import 'dart:io';

import 'dart_tutorial/addressbook.pb.dart';
import 'dart_tutorial/addressbook.pbenum.dart';

// 遍历 AddressBook 中的所有人并打印他们的信息。
void printAddressBook(AddressBook addressBook) {
  for (Person person in addressBook.people) {
    print('Person ID: ${ person.id}');
    print('  Name: ${ person.name}');
    if (person.hasEmail()) {
      print('  E-mail address:${ person.email}');
    }

    for (Person_PhoneNumber phoneNumber in person.phones) {
      switch (phoneNumber.type) {
        case Person_PhoneType.PHONE_TYPE_MOBILE:
          print('   Mobile phone #: ');
          break;
        case Person_PhoneType.PHONE_TYPE_HOME:
          print('   Home phone #: ');
          break;
        case Person_PhoneType.PHONE_TYPE_WORK:
          print('   Work phone #: ');
          break;
        default:
          print('   Unknown phone #: ');
          break;
      }
      print(phoneNumber.number);
    }
  }
}

// 从文件中读取整个通讯录，
// 并打印其中的全部信息。
main(List arguments) {
  if (arguments.length != 1) {
    print('Usage: list_person ADDRESS_BOOK_FILE');
    exit(-1);
  }

  // 读取现有的通讯录。
  File file = new File(arguments.first);
 AddressBook addressBook = new AddressBook.fromBuffer(file.readAsBytesSync());
  printAddressBook(addressBook);
}
```

## 扩展 Protobuf 消息 {#extending-a-protobuf}

在你发布（release）使用 Protobuf 消息的代码之后，你迟早会想“改进”消息的定义。如果你希望新消息向后兼容（backwards-compatible）、旧消息向前兼容（forward-compatible）——你几乎肯定希望如此——那么需要遵守一些规则。在消息的新版本中：

-   你*不得*更改任何现有字段的字段编号。
-   你*可以*删除字段。
-   你*可以*添加新字段，但必须使用全新的字段编号（也就是说，这些编号在此消息中从未被使用过，连已删除字段用过的也不行）。

（这些规则有[一些例外](/programming-guides/proto3#updating)，但极少使用。）

只要遵守这些规则，旧代码就能顺利读取新消息，并直接忽略所有新字段。对旧代码而言，被删除的单数（singular）字段只会呈现其默认值，被删除的 repeated 字段则为空。新代码也能透明地读取旧消息。

不过请记住，旧消息中不会包含新字段，因此你需要对默认值做合理的处理。会使用类型相关的[默认值](/programming-guides/proto3#default)：字符串的默认值是空字符串，布尔值的默认值是 false，数值类型的默认值是 0。
