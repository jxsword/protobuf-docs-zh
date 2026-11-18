+++
title = "Protobuf 基础：C++"
weight = 210
linkTitle = "C++"
description = "面向 C++ 程序员的 Protobuf 使用基础入门。"
type = "docs"
source_url = "https://protobuf.dev/getting-started/cpptutorial/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-18"
status = "translated"
translator = "agent"
+++

本教程为 C++ 程序员提供使用 Protobuf 的基础入门，并通过逐步创建一个简单的示例应用，向你展示如何：

-   在 `.proto` 文件中定义消息（message）格式。
-   使用 Protobuf 编译器。
-   使用 C++ Protobuf API 写入和读取消息。

本文并不是一份在 C++ 中使用 Protobuf 的全面指南。如需更详细的参考信息，请参阅 [Protobuf 语言指南](/programming-guides/editions)、[C++ API 参考](/reference/cpp/api-docs)、[C++ 生成代码指南](/reference/cpp/cpp-generated)以及[编码参考](/programming-guides/encoding)。

## 问题域 {#problem-domain}

我们要使用的示例是一个非常简单的“通讯录”应用，它可以把人们的联系信息写入文件，也可以从文件中读出。通讯录中的每个人都有姓名、ID、电子邮件地址和联系电话。

如何对这样的结构化数据（structured data）进行序列化（serialization）并读取出来？有以下几种解决办法：

-   可以把内存中的原始数据结构以二进制形式发送/保存。随着时间推移，这种做法非常脆弱，因为接收/读取代码必须以完全相同的内存布局、字节序（endianness）等条件来编译。此外，随着文件不断累积原始格式的数据、为该格式定制的软件副本四处散布，日后要扩展这种格式会非常困难。
-   你可以自行发明一种临时方式，把各数据项编码进单个字符串——例如把 4 个整数编码成 “12:3:-23:67”。这种方式简单而灵活，但需要专门编写一次性的编码与解析（parse）代码，而且解析会带来少量运行时开销。它最适合用于编码非常简单的数据。
-   将数据序列化为 XML。这种方式颇具吸引力，因为 XML（勉强）算是人类可读的，而且许多语言都有绑定库。如果你希望与其他应用/项目共享数据，这可能是个不错的选择。然而，XML 以极度占用空间而著称，对其进行编码/解码可能给应用带来巨大的性能损失。此外，遍历 XML DOM 树通常也比访问类中的简单字段（field）复杂得多。

除了这些方案之外，你还可以使用 Protobuf。Protobuf 正是为解决这一问题而生的灵活、高效、自动化方案。使用 Protobuf 时，你要为想要存储的数据结构编写一份 `.proto` 描述。Protobuf 编译器会据此创建一个类，以高效的二进制格式（binary format）实现 Protobuf 数据的自动编码与解析。生成的类为构成 Protobuf 消息的字段提供 getter 和 setter，并负责把消息作为一个整体进行读写时的各项细节。重要的是，Protobuf 格式支持随时间推移扩展格式，同时代码仍能读取以旧格式编码的数据。

## 在哪里找到示例代码 {#example-code}

示例代码包含在源码包中，位于 [“examples” 目录](https://github.com/protocolbuffers/protobuf/tree/main/examples)下。

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
    PhoneType type = 2;
  }

  repeated PhoneNumber phones = 4;
}

message AddressBook {
  repeated Person people = 1;
}

```

可以看到，其语法与 C++ 或 Java 相似。下面我们逐部分过一遍这个文件，看看各部分的作用。

`.proto` 文件以一条 `edition` 声明开头。版次（edition）取代了旧的 `syntax = "proto2"` 和 `syntax = "proto3"` 声明，为语言随时间的演进提供了更灵活的方式。

接下来是一条 package 声明，它有助于避免不同项目之间的命名冲突。在 C++ 中，生成的类会被放置在与 package 名称匹配的命名空间（namespace）中。

package 声明之后是你的消息定义。消息只是一个包含一组带类型字段的聚合体（aggregate）。许多标准简单数据类型都可用作字段类型，包括 `bool`、`int32`、`float`、`double` 和 `string`。你还可以把其他消息类型用作字段类型，为消息添加更深层的结构——在上面的示例中，`Person` 消息包含 `PhoneNumber` 消息，而 `AddressBook` 消息包含 `Person` 消息。你甚至可以把消息类型嵌套定义在其他消息内部——如你所见，`PhoneNumber` 类型就定义在 `Person` 之中。如果希望某个字段的取值限定在一组预定义值之内，你还可以定义枚举（enum）类型——这里的目的是指定电话号码可以是若干类型之一。

每个元素上的 “ = 1”、“ = 2” 标记，标识出该字段在二进制编码中使用的唯一字段编号。字段编号 1-15 比更大的编号少用一个字节来编码，因此作为一种优化，你可以决定把 1-15 这些编号用于常用或可重复（repeated）的元素，而把 16 及以上的字段编号留给不那么常用的元素。

字段可以是以下几种类型之一：

*   单数（singular）：默认情况下，字段是可选的（optional），也就是说字段可以设置，也可以不设置。如果 singular 字段未被设置，就会使用类型相关的默认值：数值类型为 0，字符串为空字符串，布尔类型为 false，枚举为第一个定义的枚举值（必须为 0）。注意，你无法把一个字段显式设置为 `singular`；它只是对“非重复字段”的一种描述。

*   **`repeated`**：字段可以重复任意多次（包括零次）。重复值的顺序会得到保留。可以把 repeated 字段看作大小动态可变的数组。

在 Protobuf 的旧版本中曾存在 `required` 关键字，但人们发现它十分脆弱，因此在 Protobuf 的现代版本中已不再支持（不过版次机制确实提供了一个特性（feature），出于向后兼容（backward compatibility）的考虑可以用它来启用该关键字）。

关于编写 `.proto` 文件的完整指南——包括所有可能的字段类型——请参阅 [Protobuf 语言指南](/programming-guides/editions)。不过，不要去找类似类继承的机制——Protobuf 并不支持这种做法。

## 编译你的 Protobuf 模式（schema）{#compiling-protocol-buffers}

现在你已经有 `.proto` 文件了，接下来要做的就是生成读写 `AddressBook`（因而也包括 `Person` 和 `PhoneNumber`）消息所需的类。为此，你需要用 Protobuf 编译器 `protoc` 编译你的 `.proto`：

1.  如果尚未安装编译器，请按照 [Protobuf 编译器安装](/installation/)中的说明操作。

2.  现在运行编译器，指定源目录（你的应用源码所在的位置——如果未提供该值，则使用当前目录）、目标目录（希望生成的代码存放的位置；通常与 `$SRC_DIR` 相同），以及你的 `.proto` 的路径。在本例中，应执行以下命令：

    ```shell
    protoc -I=$SRC_DIR --cpp_out=$DST_DIR $SRC_DIR/addressbook.proto
    ```

    由于你想要的是 C++ 类，因此要使用 `--cpp_out` 选项——其他受支持的语言也提供了类似的选项。

这会在你指定的目标目录中生成以下文件：

-   `addressbook.pb.h`，声明生成的类的头文件。
-   `addressbook.pb.cc`，包含这些类的实现。

## Protobuf API {#protobuf-api}

我们来看看部分生成代码，了解一下编译器为你创建了哪些类和函数。打开 `addressbook.pb.h` 可以看到，你在 `addressbook.proto` 中指定的每个消息都对应一个类。仔细观察 `Person` 类可以发现，编译器为每个字段都生成了访问器（accessor）。例如，对于 `name`、`id`、`email` 和 `phones` 字段，你有以下方法：

```cpp
  // name
  bool has_name() const; // 仅适用于显式存在性（explicit presence）的字段
  void clear_name();
  const ::std::string& name() const;
  void set_name(const ::std::string& value);
  ::std::string* mutable_name();

  // id
  bool has_id() const;
  void clear_id();
  int32_t id() const;
  void set_id(int32_t value);

  // email
  bool has_email() const;
  void clear_email();
  const ::std::string& email() const;
  void set_email(const ::std::string& value);
  ::std::string* mutable_email();

  // phones
  int phones_size() const;
  void clear_phones();
  const ::google::protobuf::RepeatedPtrField< ::tutorial::Person_PhoneNumber >& phones() const;
  ::google::protobuf::RepeatedPtrField< ::tutorial::Person_PhoneNumber >* mutable_phones();
  const ::tutorial::Person_PhoneNumber& phones(int index) const;
  ::tutorial::Person_PhoneNumber* mutable_phones(int index);
  ::tutorial::Person_PhoneNumber* add_phones();
```

可以看到，getter 的名称与字段完全相同（小写形式），而 setter 方法以 `set_` 开头。对于具有显式存在性（explicit presence）追踪的单数字段，还有对应的 `has_` 方法——如果该字段已被设置，它们会返回 true。最后，每个字段都有一个 `clear_` 方法，用于把字段重新置回未设置的默认状态。

数值类型的 `id` 字段只有上述的基本访问器集合，而 `name` 和 `email` 字段由于是字符串，还多了几个方法：一个 `mutable_` getter，让你能拿到指向该字符串的直接指针；以及一个额外的 setter。注意，即使 `email` 尚未设置，你也可以调用 `mutable_email()`；它会自动初始化为空字符串。如果本示例中有 repeated 的消息字段，它也会有 `mutable_` 方法，但没有 `set_` 方法。

repeated 字段还有一些特殊方法——查看 repeated 字段 `phones` 的方法，你会发现你可以：

-   检查 repeated 字段的 `_size`（换句话说，即与该 `Person` 关联的电话号码数量）。
-   通过索引获取指定的电话号码。
-   更新指定索引处的现有电话号码。
-   向消息中添加另一个电话号码，然后对其进行编辑（repeated 标量（scalar）类型有一个 `add_` 方法，只需传入新值即可）。

关于协议编译器针对任何特定字段定义究竟会生成哪些成员的详细信息，请参阅 [C++ 生成代码参考](/reference/cpp/cpp-generated)。

### 枚举与嵌套类 {#enums-nested-classes}

生成代码中包含一个与你的 `.proto` 枚举相对应的 `PhoneType` 枚举。你可以把这个类型写作 `Person::PhoneType`，把它的值写作 `Person::PHONE_TYPE_MOBILE`、`Person::PHONE_TYPE_HOME` 和 `Person::PHONE_TYPE_WORK`（其实现细节稍微复杂一些，但要使用这个枚举，你并不需要理解这些细节）。

编译器还为你生成了一个名为 `Person::PhoneNumber` 的嵌套类（nested class）。查看代码可以发现，“真正的”类实际上叫做 `Person_PhoneNumber`，但 `Person` 内部定义的一个 typedef 让你可以把它当作嵌套类来使用。唯一会有差别的情况是：如果你想在另一个文件中前向声明（forward-declare）这个类——在 C++ 中你不能前向声明嵌套类型，但可以前向声明 `Person_PhoneNumber`。

### 标准消息方法 {#standard-message-methods}

每个消息类还包含许多其他方法，可用于检查或操作整个消息，包括：

-   `bool IsInitialized() const;`：检查是否所有 required 字段都已设置。
-   `string DebugString() const;`：返回消息的人类可读表示形式，对调试特别有用。
-   `void CopyFrom(const Person& from);`：用给定消息的值覆盖当前消息。
-   `void Clear();`：把所有元素清空回空状态。

这些方法以及下一节描述的 I/O 方法，共同实现了所有 C++ Protobuf 类共享的 `Message` 接口。更多信息请参阅 [`Message` 的完整 API 文档](/reference/cpp/api-docs/google.protobuf.message#Message)。

### 解析与序列化 {#parsing-serialization}

最后，每个 Protobuf 类都有一些方法，用于通过 Protobuf [二进制格式](/programming-guides/encoding)写入和读取你所选类型的消息。这些方法包括：

-   `bool SerializeToString(string* output) const;`：序列化该消息，并把字节存入给定的 string。注意，这些字节是二进制的，而不是文本；我们只是把 `string` 类当作一个方便的容器来使用。
-   `bool ParseFromString(const string& data);`：从给定的字符串解析出一条消息。
-   `bool SerializeToOstream(ostream* output) const;`：把消息写入给定的 C++ `ostream`。
-   `bool ParseFromIstream(istream* input);`：从给定的 C++ `istream` 解析出一条消息。

这些只是用于解析和序列化的众多选项中的几个。完整列表请参阅 [`Message` API 参考](/reference/cpp/api-docs/google.protobuf.message#Message)。

{{% alert title="Important" color="warning" %}} **Protobuf 与面向对象设计**
Protobuf 类基本上只是数据载体（类似于 C 语言中的 struct），并不提供额外的功能；在对象模型中，它们并不适合作为一等公民。如果你想为生成的类添加更丰富的行为，最好的做法是把生成的 Protobuf 类包装在一个应用特定的类中。如果你无法控制 .proto 文件的设计（例如你在复用另一个项目的文件），把 Protobuf 消息包装起来也是个好主意。在这种情况下，你可以利用包装类来打造一个更适合你的应用独特环境的接口：隐藏部分数据和方法、暴露便捷函数等等。**你无法通过继承生成的类来为其添加行为**，因为它们是 final 的。这样做既能避免破坏内部机制，本来也不符合良好的面向对象实践。

{{% /alert %}}

## 写入消息 {#writing-a-message}

现在我们来试用你的 Protobuf 类。你希望通讯录应用实现的第一件事，就是把个人信息写入通讯录文件。为此，你需要创建并填充 Protobuf 类的实例，然后把它们写入输出流。

下面这个程序会从文件中读取 `AddressBook`，根据用户输入向其中添加一个新的 `Person`，然后把新的 `AddressBook` 重新写回文件。其中直接调用或引用协议编译器所生成代码的部分已突出显示。

```cpp
#include <iostream>
#include <fstream>
#include <string>
#include "addressbook.pb.h"
using namespace std;

// 此函数根据用户输入填充一条 Person 消息。
void PromptForAddress(tutorial::Person& person) {
  cout << "Enter person ID number: ";
  int id;
  cin >> id;
  person.set_id(id);
  cin.ignore(256, '\n');

  cout << "Enter name: ";
  getline(cin, *person.mutable_name());

  cout << "Enter email address (blank for none): ";
  string email;
  getline(cin, email);
  if (!email.empty()) {
    person.set_email(email);
  }

  while (true) {
    cout << "Enter a phone number (or leave blank to finish): ";
    string number;
    getline(cin, number);
    if (number.empty()) {
      break;
    }

    tutorial::Person::PhoneNumber* phone_number = person.add_phones();
    phone_number->set_number(number);

    cout << "Is this a mobile, home, or work phone? ";
    string type;
    getline(cin, type);
    if (type == "mobile") {
      phone_number->set_type(tutorial::Person::PHONE_TYPE_MOBILE);
    } else if (type == "home") {
      phone_number->set_type(tutorial::Person::PHONE_TYPE_HOME);
    } else if (type == "work") {
      phone_number->set_type(tutorial::Person::PHONE_TYPE_WORK);
    } else {
      cout << "Unknown phone type. Using default." << endl;
    }
  }
}

// main 函数：从文件中读取整个通讯录，
//   根据用户输入添加一个人，然后把结果写回同一个文件。
int main(int argc, char* argv[]) {
  // 验证我们链接的库版本与编译时所用的头文件版本是否兼容。
  GOOGLE_PROTOBUF_VERIFY_VERSION;

  if (argc != 2) {
    cerr << "Usage:  " << argv[0] << " ADDRESS_BOOK_FILE" << endl;
    return -1;
  }

  tutorial::AddressBook address_book;

  {
    // 读取现有的通讯录。
    fstream input(argv[1], ios::in | ios::binary);
    if (!input) {
      cout << argv[1] << ": File not found.  Creating a new file." << endl;
    } else if (!address_book.ParseFromIstream(&input)) {
      cerr << "Failed to parse address book." << endl;
      return -1;
    }
  }

  // 添加一条地址。
  PromptForAddress(*address_book.add_people());

  {
    // 把新的通讯录写回磁盘。
    fstream output(argv[1], ios::out | ios::trunc | ios::binary);
    if (!address_book.SerializeToOstream(&output)) {
      cerr << "Failed to write address book." << endl;
      return -1;
    }
  }

  // 可选：删除 libprotobuf 分配的所有全局对象。
  google::protobuf::ShutdownProtobufLibrary();

  return 0;
}
```

注意 `GOOGLE_PROTOBUF_VERIFY_VERSION` 宏。在使用 C++ Protobuf 库之前先执行这个宏是一种良好实践——尽管并非严格必需。它会验证你没有意外链接到与你编译时所用的头文件版本不兼容的库版本。一旦检测到版本不匹配，程序就会中止。注意，每个 `.pb.cc` 文件都会在启动时自动调用这个宏。

另外请注意程序末尾对 `ShutdownProtobufLibrary()` 的调用。它所做的只是删除 Protobuf 库分配的所有全局对象。对大多数程序而言这并非必需，因为进程反正都要退出，操作系统会负责回收其全部内存。然而，如果你使用的内存泄漏检查工具要求释放每一个对象，或者你正在编写一个可能被单个进程多次加载和卸载的库，那么你可能希望强制 Protobuf 清理所有内容。

## 读取消息 {#reading-a-message}

当然，如果无法从中取出任何信息，通讯录就没多大用处了！本示例读取由上一个示例创建的文件，并打印其中的所有信息。

```cpp
#include <iostream>
#include <fstream>
#include <string>
#include "addressbook.pb.h"
using namespace std;

// 遍历 AddressBook 中的所有人并打印他们的信息。
void ListPeople(const tutorial::AddressBook& address_book) {
  for (const tutorial::Person& person : address_book.people()) {
    cout << "Person ID: " << person.id() << endl;
    cout << "  Name: " << person.name() << endl;
    if (!person.has_email()) {
      cout << "  E-mail address: " << person.email() << endl;
    }

    for (const tutorial::Person::PhoneNumber& phone_number : person.phones()) {
      switch (phone_number.type()) {
        case tutorial::Person::PHONE_TYPE_MOBILE:
          cout << "  Mobile phone #: ";
          break;
        case tutorial::Person::PHONE_TYPE_HOME:
          cout << "  Home phone #: ";
          break;
        case tutorial::Person::PHONE_TYPE_WORK:
          cout << "  Work phone #: ";
          break;
        case tutorial::Person::PHONE_TYPE_UNSPECIFIED:
        default:
          cout << "  Phone #: ";
          break;
      }
      cout << phone_number.number() << endl;
    }
  }
}

// main 函数：从文件中读取整个通讯录，并打印其中的全部信息。
int main(int argc, char* argv[]) {
  // 验证我们链接的库版本与编译时所用的头文件版本是否兼容。
  GOOGLE_PROTOBUF_VERIFY_VERSION;

  if (argc != 2) {
    cerr << "Usage:  " << argv[0] << " ADDRESS_BOOK_FILE" << endl;
    return -1;
  }

  tutorial::AddressBook address_book;

  {
    // 读取现有的通讯录。
    fstream input(argv[1], ios::in | ios::binary);
    if (!address_book.ParseFromIstream(&input)) {
      cerr << "Failed to parse address book." << endl;
      return -1;
    }
  }

  ListPeople(address_book);

  // 可选：删除 libprotobuf 分配的所有全局对象。
  google::protobuf::ShutdownProtobufLibrary();

  return 0;
}
```

## 扩展 Protobuf 消息 {#extending-a-protobuf}

在你发布（release）使用 Protobuf 消息的代码之后，你迟早会想“改进”消息的定义。如果你希望新消息向后兼容（backwards-compatible）、旧消息向前兼容（forward-compatible）——你几乎肯定希望如此——那么需要遵守一些规则。在消息的新版本中：

*   你*不得*更改任何现有字段的字段编号。
*   你*可以*删除单数字段或 repeated 字段。
*   你*可以*添加新的单数字段或 repeated 字段，但必须使用全新的字段编号（也就是说，这些编号在此消息中从未被使用过，连已删除字段用过的也不行）。

（这些规则有[一些例外](/programming-guides/editions#updating)，但极少使用。）

只要遵守这些规则，旧代码就能顺利读取新消息，并直接忽略所有新字段。对旧代码而言，被删除的字段只会呈现其默认值，被删除的 repeated 字段则为空。新代码也能透明地读取旧消息。不过请记住，旧消息中不会包含新字段，因此在使用它们之前，你需要通过检查字段是否为默认值（例如空字符串）来判断其是否存在。

## 优化建议 {#optimization}

C++ Protobuf 库本身已经过极为深入的优化。不过，正确的使用方式还能进一步提升性能。以下是一些榨干这个库每一分速度的技巧：

-   **使用 arena 进行内存分配。** 当你在一次短生命周期的操作（比如解析单个请求）中创建大量 Protobuf 消息时，系统的内存分配器可能成为瓶颈。arena 机制正是为缓解这一问题而设计的。通过使用 arena，你可以以较低的开销进行多次分配，并只需一次释放就能回收全部分配。在消息密集的应用中，这能显著提升性能。

    要使用 arena，你需要在一个 `google::protobuf::Arena` 对象上分配消息：

    ```cpp
    google::protobuf::Arena arena;
    tutorial::Person* person = google::protobuf::Arena::Create<tutorial::Person>(&arena);
    // ... 填充 person ...
    ```

    当 arena 对象被销毁时，在其上分配的所有消息都会被释放。更多细节请参阅 [arena 指南](/arenas)。

-   **尽可能复用非 arena 消息对象。** 消息会尽量保留自己分配过的内存以备复用，即使在被清空之后也是如此。因此，如果你要连续处理许多类型相同、结构相近的消息，最好每次都复用同一个消息对象，以减轻内存分配器的负担。不过，对象会随着时间推移变得臃肿，尤其是当你的消息“形态”多变，或者你偶尔构造出比平时大得多的消息时。你应当通过调用 `SpaceUsed` 方法监控消息对象的大小，一旦过大就将其删除。

    复用 arena 消息可能导致内存无限制增长。复用堆上的消息则更安全。不过，即便是堆上的消息，你仍可能遇到字段高水位（high water mark）方面的问题。例如，如果你看到消息：

    ```none
    a: [1, 2, 3, 4]
    b: [1]
    ```

    和

    ```none
    a: [1]
    b: [1, 2, 3, 4]
    ```

    并且复用这些消息，那么两个字段都会保留足以容纳其所见过的最大内容的内存。因此，如果每次输入只有 5 个元素，复用的消息却会为 8 个元素保留内存。

-   你系统的内存分配器在从多个线程分配大量小对象时可能优化不佳。可以尝试改用 [Google 的 TCMalloc](https://github.com/google/tcmalloc)。

## 高级用法 {#advanced-usage}

Protobuf 的用途远不止简单的访问器和序列化。请务必浏览 [C++ API 参考](/reference/cpp)，看看你还能用它做什么。

协议消息类提供的一个关键特性是*反射（reflection）*。你可以在不针对任何特定消息类型编写代码的情况下，遍历消息的字段并操作它们的值。反射的一个非常有用的用途，是在协议消息与其他编码（例如 XML 或 JSON）之间进行相互转换。反射更高级的用法，可能是找出两个同类型消息之间的差异，或者开发一种“协议消息正则表达式”，让你可以编写表达式来匹配特定的消息内容。只要发挥想象力，你就能把 Protobuf 应用到比最初预期广泛得多的问题上！

反射由 [`Message::Reflection` 接口](/reference/cpp/api-docs/google.protobuf.message#Reflection)提供。
