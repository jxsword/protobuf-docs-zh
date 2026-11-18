+++
title = "C++ Arena 内存分配指南"
weight = 520
linkTitle = "Arena 内存分配指南"
description = "arena 内存分配是一项仅限 C++ 的特性，可帮助你在使用 Protobuf 时优化内存使用并提升性能。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/arenas/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

本页确切说明在启用 arena 内存分配（arena allocation）后，Protobuf 编译器除 [C++ 生成代码指南](/reference/cpp/cpp-generated) 所述代码之外，还会生成哪些 C++ 代码。本文假定你已熟悉 [语言指南](/programming-guides/editions) 和 [C++ 生成代码指南](/reference/cpp/cpp-generated) 中的内容。

## 为什么要使用 arena 分配？{#why}

内存的分配与释放占据了 Protobuf 代码 CPU 时间的相当大一部分。默认情况下，Protobuf 会为每个消息（message）对象、消息的每个子对象以及若干字段（field）类型（例如字符串）执行堆分配（heap allocation）。这些分配会在解析消息以及在内存中构建新消息时批量发生，而相应的释放在消息及其子对象树被释放时进行。

基于 arena 的分配方式正是为降低这一性能开销而设计的。采用 arena 分配时，新对象会从一块称为 arena 的大块预分配内存中分配出来。丢弃整个 arena 即可一次性释放所有对象，理想情况下无需运行其中任何一个对象的析构函数（不过 arena 仍可在需要时维护一份“析构函数列表”）。这使得对象分配被简化为一次简单的指针递增，从而变得更快，而释放则几乎不产生任何开销。arena 分配还能提供更高的缓存效率：消息被解析时更有可能分配在连续的内存中，这使得遍历消息时更容易命中热点缓存行。

要获得这些收益，你需要留意对象的生命周期，并为 arena 的使用找到合适的粒度（对服务器而言，这通常是按请求划分）。关于如何充分利用 arena 分配的更多信息，请参阅[使用模式与最佳实践](#usage)。

下表总结了使用 arena 的典型性能优点与缺点：

操作             | 堆分配的 proto 消息                                                                                                | arena 分配的 proto 消息
:-------------------- | :--------------------------------------------------------------------------------------------------------------------------- | :-----------------------------
*消息分配*  | 平均较慢                                                                                                            | 平均较快
*消息销毁* | 平均较慢                                                                                                            | 平均较快
*消息移动*       | 始终是移动（开销等同于一次[浅拷贝](https://en.wikipedia.org/wiki/Object_copying#Shallow_copy)） | 有时为[深拷贝](https://en.wikipedia.org/wiki/Object_copying#Deep_copy)

## 入门 {#gettingstarted}

Protobuf 编译器会为文件中的消息生成支持 arena 分配的代码，如下例所示。

```cpp
#include <google/protobuf/arena.h>
{
  google::protobuf::Arena arena;
  MyMessage* message = google::protobuf::Arena::Create<MyMessage>(&arena);
  // ...
}
```

由 `Create()` 创建的消息对象，其生命周期与 `arena` 相同，你不应 `delete` 返回的消息指针。消息对象的全部内部存储（有少数例外[^1]）及其子消息（submessage）（例如 `MyMessage` 中 repeated 字段内的子消息）也同样在 arena 上分配。

在大多数情况下，你的其余代码与不使用 arena 分配时并无二致。

我们将在后续章节中更详细地介绍 arena API，你也可以在文档末尾看到一个更完整的[示例](#example)。

[^1]: 目前，即使包含它的消息位于 arena 上，字符串字段的数据仍存储在堆上。未知字段（unknown fields）也是堆分配的。

## Arena 类 API {#arenaclass}

你使用 [`google::protobuf::Arena`](/reference/cpp/api-docs/google.protobuf.arena) 类在 arena 上创建消息对象。该类实现了以下公共方法。

### 构造函数 {#constructors}

-   `Arena()`：使用默认参数创建一个新的 arena，这些参数针对一般用例做了调优。
-   `Arena(const ArenaOptions& options)`：使用指定的分配选项创建一个新的 arena。`ArenaOptions` 中可用的选项包括：在退回到系统分配器之前，先使用用户提供的初始内存块进行分配；控制内存块的初始请求大小与最大请求大小；以及允许传入自定义的内存块分配与释放函数指针，以便在这些块之上构建空闲列表（freelist）等结构。

### 分配方法 {#allocation}

*   `template<typename T> static T* Create(Arena* arena)` 或 `template<typename T> static T* Create(Arena* arena, args...)`

    *   如果 `T` 是完全兼容（fully compatible）的类型[^footnote]，则该方法会在 arena 上创建类型为 `T` 的新 Protobuf 消息对象及其子对象。

        如果 `arena` 不为 NULL，返回的对象将在 arena 上分配，其内部存储与子类型（如有）也将分配在同一个 arena 上，其生命周期与该 arena 相同。不得手动 delete/释放该对象：就生命周期而言，该对象由 arena 拥有。

        如果 `arena` 为 NULL，返回的对象将在堆上分配，返回后由调用者拥有该对象。

    *   如果 `T` 是用户自定义类型，该方法允许你在 arena 上创建对象，但不创建其子对象。例如，假设你有这样一个 C++ 类：

        ```cpp
        class MyCustomClass {
            MyCustomClass(int arg1, int arg2);
            // ...
        };
        ```

        ……你可以像下面这样在 arena 上创建它的实例：

        ```cpp
        void func() {
            // ...
            google::protobuf::Arena arena;
            MyCustomClass* c = google::protobuf::Arena::Create<MyCustomClass>(&arena, constructor_arg1, constructor_arg2);
            // ...
        }
        ```

-   `template<typename T> static T* CreateArray(Arena* arena, size_t n)`：如果 `arena` 不为 NULL，该方法为 `n` 个类型为 `T` 的元素分配原始存储空间并将其返回。arena 拥有返回的内存，并会在自身销毁时将其释放。如果 `arena` 为 NULL，该方法在堆上分配存储空间，调用者获得所有权。

    `T` 必须具有平凡构造函数（trivial constructor）：在 arena 上创建数组时，构造函数不会被调用。

[^footnote]: 一个类型要成为“完全兼容”（fully compatible）类型需要满足哪些条件，属于 Protobuf 库的内部实现细节，不应假定其可靠。

### “所有权列表”（owned list）方法 {#owned-list}

以下方法允许你将特定对象或析构函数指定为由 arena“拥有”（owned），从而确保当 arena 本身被删除时，这些对象会被删除、这些析构函数会被调用。

-   `template<typename T> void Own(T* object)`：将 `object` 加入 arena 所拥有的堆对象列表。当 arena 被销毁时，它会遍历该列表，并使用 operator delete（即系统内存分配器）释放每个对象。当某个对象的生命周期需要与 arena 绑定，但由于某种原因无法或尚未在 arena 上分配时，此方法非常有用。
-   `template<typename T> void OwnDestructor(T* object)`：将 `object` 的析构函数加入 arena 待调用的析构函数列表。当 arena 被销毁时，它会遍历该列表并依次调用每个析构函数。它不会尝试释放 object 的底层内存。当某个对象内嵌于 arena 分配的存储中，而其析构函数不会被以其他方式调用时（例如，其所在类是一个析构函数不会被调用的 Protobuf 消息，或者它是在由 `AllocateArray()` 分配的内存块中手动构造的），此方法非常有用。

### 其他方法 {#other-methods}

-   `uint64 SpaceUsed() const`：返回 arena 的总大小，即底层各内存块大小之和。此方法是线程安全的；但如果多个线程存在并发分配，该方法的返回值可能不包含那些新内存块的大小。
-   `uint64 Reset()`：销毁 arena 的存储：先调用所有已注册的析构函数并释放所有已注册的堆对象，然后丢弃所有 arena 内存块。这一清理过程与 arena 析构函数运行时的过程等效，区别在于该方法返回后 arena 仍可复用于新的分配。该方法返回 arena 使用的总大小：这一信息有助于调优性能。
-   `template<typename T> Arena* GetArena()`：返回指向此 arena 的指针。它本身没有太大用处，但可以让 `Arena` 用在期望存在 `GetArena()` 方法的模板实例化中。

### 线程安全 {#thread-safety}

`google::protobuf::Arena` 的分配方法是线程安全的，底层实现也尽力使多线程分配保持高效。`Reset()` 方法*不是*线程安全的：执行 arena 重置的线程必须先与所有正在执行分配或正在使用从该 arena 分配的对象的线程同步。

## 生成的消息类 {#messageclass}

启用 arena 分配后，以下消息类成员会被更改或新增。

### 消息类方法 {#message-class-methods}

-   `Message(Message&& other)`：如果源消息不在 arena 上，移动构造函数会高效地把所有字段从一个消息*移动*到另一个消息，不产生副本或堆分配（此操作的时间复杂度为 `O(number-of-declared-fields)`）。但如果源消息位于 arena 上，它会对底层数据执行*深拷贝*。两种情况下，源消息都会处于有效但未指定的状态。
-   `Message& operator=(Message&& other)`：如果两个消息都不在 arena 上，或位于*同一个* arena 上，移动赋值运算符会高效地把所有字段从一个消息*移动*到另一个消息，不产生副本或堆分配（此操作的时间复杂度为 `O(number-of-declared-fields)`）。但如果只有一个消息位于 arena 上，或两个消息位于不同的 arena 上，它会对底层数据执行*深拷贝*。两种情况下，源消息都会处于有效但未指定的状态。
-   `void Swap(Message* other)`：如果待交换的两个消息都不在 arena 上，或位于*同一个* arena 上，[`Swap()`](/reference/cpp/cpp-generated#message) 的行为与未启用 arena 分配时相同：它高效地交换消息对象的内容，几乎完全通过廉价的指针交换完成，避免了拷贝。但如果只有一个消息位于 arena 上，或两个消息位于不同的 arena 上，`Swap()` 会对底层数据执行*深拷贝*。这一新行为是必要的：否则，被交换的子对象可能拥有不同的生命周期，进而可能导致释放后使用（use-after-free）缺陷。
-   `Message* New(Arena* arena)`：标准 `New()` 方法的另一种重载形式。它允许在给定的 arena 上创建该类型的新消息对象。如果调用它的具体消息类型是以启用 arena 分配的方式生成的，其语义与 `Arena::Create<T>(arena)` 完全相同。如果该消息类型不是以启用 arena 分配的方式生成的，那么在 `arena` 不为 NULL 时，它等效于先进行一次普通分配，随后调用 `arena->Own(message)`。
-   `Arena* GetArena()`：返回此消息对象所分配在的 arena（如果有的话）。
-   `void UnsafeArenaSwap(Message* other)`：与 `Swap()` 相同，但它假定两个对象位于同一个 arena 上（或都不在 arena 上），并始终使用该操作的高效指针交换实现。使用此方法可以提升性能：与 `Swap()` 不同，它在执行交换前无需检查各消息位于哪个 arena 上。正如 `Unsafe` 前缀所提示的，只有在你确信要交换的消息不在不同的 arena 上时才应使用此方法；否则该方法可能产生不可预测的结果。

### 内嵌消息字段 {#arenaembeddedmessage}

当你在 arena 上分配消息对象时，其内嵌消息字段（embedded message field）对象（即子消息）也会自动由该 arena 拥有。这些消息对象如何分配，取决于它们是在哪里定义的：

-   如果该消息类型同样定义在启用了 arena 分配的 `.proto` 文件中，对象将直接在 arena 上分配。
-   如果该消息类型来自另一个未启用 arena 分配的 `.proto` 文件，对象将在堆上分配，但由父消息的 arena“拥有”。这意味着当 arena 被销毁时，该对象会随 arena 上的对象一起被释放。

对于字段定义：

```proto
Bar foo = 1;
```

启用 arena 分配后，以下方法会被新增，或具有某些特殊行为。否则，访问器（accessor）方法仅使用[默认行为](/reference/cpp/cpp-generated#embeddedmessage)。

-   `Bar* mutable_foo()`：返回指向子消息实例的可变指针。如果父对象位于 arena 上，返回的对象也会位于 arena 上。
-   `void set_allocated_foo(Bar* bar)`：接收一个新对象，并将其采纳为该字段的新值。当对象跨越 arena/arena 或 arena/堆边界时，arena 支持会添加额外的拷贝语义以维持正确的所有权：
    -   如果父对象位于堆上且 `bar` 位于堆上，或者父对象与该消息位于同一个 arena 上，此方法的行为不变。
    -   如果父对象位于 arena 上而 `bar` 位于堆上，父消息会通过 `arena->Own()` 将 `bar` 加入其 arena 的所有权列表。
    -   如果父对象位于 arena 上而 `bar` 位于另一个 arena 上，此方法会制作该消息的一个副本，并把副本作为新的字段值。
-   `Bar* release_foo()`：返回该字段现有的子消息实例（如果已设置），未设置则返回 NULL 指针，同时将该实例的所有权移交给调用者（release），并清空父消息的字段。为了维持“返回的对象始终是*堆分配*的”这一契约，arena 支持添加了额外的拷贝语义：
    -   如果父消息位于 arena 上，此方法会在堆上制作该子消息的一个副本，清空字段值，并返回该副本。
    -   如果父消息位于堆上，此方法的行为不变。
-   `void unsafe_arena_set_allocated_foo(Bar* bar)`：与 `set_allocated_foo` 相同，但它假定父对象与子消息位于同一个 arena 上。使用此版本的方法可以提升性能，因为它无需检查消息位于特定的 arena 还是堆上。有关安全使用方式的细节，请参阅 [allocated/release 模式](#set-allocated)。
-   `Bar* unsafe_arena_release_foo()`：与 `release_foo()` 类似，但会跳过所有所有权检查。有关安全使用方式的细节，请参阅 [allocated/release 模式](#set-allocated)。

### 字符串字段 {#arenastring}

即使父消息位于 arena 上，字符串字段的数据仍存储在堆上。因此，即使启用了 arena 分配，字符串访问器方法仍使用[默认行为](/reference/cpp/cpp-generated#string)。

### repeated 字段 {#arenarepeated}

当包含它的消息采用 arena 分配时，repeated 字段会在 arena 上分配其内部数组存储；当元素是由指针持有的独立对象（消息或字符串）时，元素也会在 arena 上分配。在消息类层面，为 repeated 字段生成的方法没有变化。但在启用 arena 支持后，由访问器返回的 `RepeatedField` 和 `RepeatedPtrField` 对象确实会有新增方法和经修改的语义。

#### repeated 数值字段 {#repeated-numeric}

包含原始类型（primitive types）的 `RepeatedField` 对象在启用 arena 分配后具有以下新增/变更的方法：

-   `void UnsafeArenaSwap(RepeatedField* other)`：交换 `RepeatedField` 的内容，但不校验此 repeated 字段与 other 是否位于同一个 arena 上。如果不是，则两个 repeated 字段对象必须位于生命周期等效的 arena 上。一个位于 arena 上而另一个位于堆上的情形会被检查并禁止。
-   `void Swap(RepeatedField* other)`：检查每个 repeated 字段对象的 arena；如果一个位于 arena 上而另一个位于堆上，或者两者都位于 arena 上但不是同一个 arena，则会在交换发生前复制底层数组。这意味着交换完成后，每个 repeated 字段对象持有的数组都位于各自相应的 arena 或堆上。

#### repeated 内嵌消息字段 {#repeated-embedded}

包含消息的 `RepeatedPtrField` 对象在启用 arena 分配后具有以下新增/变更的方法。

-   `void UnsafeArenaSwap(RepeatedPtrField* other)`：交换 `RepeatedPtrField` 的内容，但不校验此 repeated 字段与 other 是否具有相同的 arena 指针。如果不相同，则两个 repeated 字段对象的 arena 指针必须具有等效的生命周期。一个具有非 NULL arena 指针而另一个具有 NULL arena 指针的情形会被检查并禁止。
-   `void Swap(RepeatedPtrField* other)`：检查每个 repeated 字段对象的 arena 指针；如果一个为非 NULL（内容位于 arena 上）而另一个为 NULL（内容位于堆上），或者两者都为非 NULL 但值不同，则会在交换发生前复制底层数组及其指向的对象。这意味着交换完成后，每个 repeated 字段对象持有的数组都位于各自相应的 arena 或堆上。
-   `void AddAllocated(SubMessageType* value)`：检查所提供的消息对象是否与该 repeated 字段的 arena 指针位于同一个 arena 上。

    *   源和目标都采用 arena 分配且位于同一个 arena 上：对象指针被直接加入底层数组。
    *   源和目标都采用 arena 分配但位于不同的 arena 上：会制作一个副本；如果原件是堆分配的，则将其释放，并把副本放入数组。
    *   源是堆分配的而目标是 arena 分配的：不制作副本。
    *   源是 arena 分配的而目标是堆分配的：会制作一个副本并放入数组。
    *   源和目标都是堆分配的：对象指针被直接加入底层数组。

    这维持了如下不变量：repeated 字段所指向的所有对象，都与该 repeated 字段的 arena 指针所指示的所有权域（堆或特定 arena）保持一致。

-   `SubMessageType* ReleaseLast()`：返回一个堆分配的消息，它等同于该 repeated 字段中的最后一个消息，并将该消息从 repeated 字段中移除。如果该 repeated 字段自身的 arena 指针为 NULL（因而其指向的所有消息都是堆分配的），此方法直接返回指向原对象的指针。否则，如果该 repeated 字段具有非 NULL 的 arena 指针，此方法会制作一个堆分配的副本并返回该副本。两种情况下，调用者都获得一个堆分配对象的所有权，并负责删除该对象。

-   `void UnsafeArenaAddAllocated(SubMessageType* value)`：与 `AddAllocated()` 类似，但不执行堆/arena 检查，也不进行任何消息拷贝。它把提供的指针直接加入此 repeated 字段的内部指针数组。有关安全使用方式的细节，请参阅 [allocated/release 模式](#set-allocated)。

-   `SubMessageType* UnsafeArenaReleaseLast()`：与 `ReleaseLast()` 类似，但不执行任何拷贝，即使该 repeated 字段具有非 NULL 的 arena 指针也是如此。它直接返回对象在该 repeated 字段中原有的指针。有关安全使用方式的细节，请参阅 [allocated/release 模式](#set-allocated)。

-   `void ExtractSubrange(int start, int num, SubMessageType** elements)`：从索引 `start` 开始，从该 repeated 字段中移除 `num` 个元素；如果 `elements` 不为 NULL，则将它们返回到 `elements` 中。如果该 repeated 字段位于 arena 上且需要返回元素，则会先把元素复制到堆上。两种情况下（无论有无 arena），返回的对象都位于堆上，由调用者拥有。

-   `void UnsafeArenaExtractSubrange(int start, int num, SubMessageType** elements)`：从索引 `start` 开始，从该 repeated 字段中移除 `num` 个元素；如果 `elements` 不为 NULL，则将它们返回到 `elements` 中。与 `ExtractSubrange()` 不同，此方法从不复制被提取的元素。有关安全使用方式的细节，请参阅 [allocated/release 模式](#set-allocated)。

#### repeated 字符串字段 {#repeated-string}

字符串类型的 repeated 字段与消息类型的 repeated 字段具有相同的新增方法和经修改的语义，因为它们同样通过指针引用来维护其底层对象（即字符串）。

## 使用模式与最佳实践 {#usage}

使用 arena 分配的消息时，有若干使用模式可能导致意外的拷贝或其他负面性能影响。在针对 arena 改造代码时，你应留意以下可能需要调整的常见模式。（请注意，我们在 API 设计中已尽力确保行为仍然正确——但更高性能的方案可能需要一些重构。）

### 意外拷贝 {#unintended}

有几种方法在不使用 arena 分配时从不创建对象副本，而在启用 arena 支持后却可能最终这样做。只要确保对象得到恰当的分配，并且/或者使用提供的 arena 专用方法版本，就可以避免这些多余的拷贝，下文将更详细地说明。

#### Set Allocated/Add Allocated/Release {#set-allocated}

默认情况下，针对单数消息字段（singular message field）的 `release_field()` 和 `set_allocated_field()` 方法，以及针对 repeated 消息字段的 `ReleaseLast()` 和 `AddAllocated()` 方法，允许用户代码直接附加和分离子消息，传递指针所有权而不复制任何数据。

然而，当父消息位于 arena 上时，这些方法现在有时需要复制传入或返回的对象，以维持与既有所有权契约的兼容性。更具体地说，取得所有权的方法（`set_allocated_field()` 和 `AddAllocated()`）在父对象位于 arena 上而新子对象不在（或相反），或两者位于不同的 arena 上时，可能会复制数据。移交所有权的方法（`release_field()` 和 `ReleaseLast()`）在父对象位于 arena 上时可能会复制数据，因为按照契约，返回的对象必须位于堆上。

为了避免此类拷贝，我们为这些方法添加了对应的“unsafe arena”版本，在这些版本中**绝不**执行拷贝：`unsafe_arena_set_allocated_field()`、`unsafe_arena_release_field()`、`UnsafeArenaAddAllocated()` 和 `UnsafeArenaRelease()`，分别用于单数字段和 repeated 字段。只有在你确知这样做是安全的情况下才应使用这些方法。这些方法有两种常见使用模式：

-   在同一个 arena 的不同部分之间移动消息树。注意，这种情形下消息必须位于同一个 arena 上才是安全的。
-   将一个已拥有的消息临时“出借”给一棵消息树，以避免拷贝。将一个不安全的 *add*/*set* 方法与一个不安全的 *release* 方法配对使用，无论两个消息各自的所有权方式如何，都能以尽可能低的开销完成出借（当它们位于同一个 arena、不同 arena 或根本没有 arena 时，此模式都有效）。注意，在不安全的 *add*/*set* 与其对应的 *release* 之间：借用方不得被交换、移动、清空或销毁；被出借的消息不得被交换或移动；借用方不得清空或释放被出借的消息；被出借的消息不得被销毁。

下面这个例子展示了如何用这些方法避免不必要的拷贝。假设你已在一个 arena 上创建了以下消息。

```cpp
Arena* arena = new google::protobuf::Arena();
MyFeatureMessage* arena_message_1 =
  google::protobuf::Arena::Create<MyFeatureMessage>(arena);
arena_message_1->mutable_nested_message()->set_feature_id(11);

MyFeatureMessage* arena_message_2 =
  google::protobuf::Arena::Create<MyFeatureMessage>(arena);
```

下面的代码对 `release_...()` API 的使用是低效的：

```cpp
arena_message_2->set_allocated_nested_message(arena_message_1->release_nested_message());

arena_message_1->release_message(); // 返回底层 nested_message 的副本，并删除底层指针
```

改用“unsafe arena”版本则可以避免这次拷贝：

```cpp
arena_message_2->unsafe_arena_set_allocated_nested_message(
   arena_message_1->unsafe_arena_release_nested_message());
```

你可以在上文的[内嵌消息字段](#arenaembeddedmessage)一节中进一步了解这些方法。

#### Swap {#swap}

当使用 `Swap()` 交换两个消息的内容时，如果两个消息位于不同的 arena 上，或者一个位于 arena 上而另一个位于堆上，底层子对象可能会被复制。如果你想避免这种复制，并且 (i) 确知这两个消息位于同一个 arena 上，或者虽然位于不同 arena 但这些 arena 的生命周期等效，或者 (ii) 确知这两个消息都位于堆上，就可以使用新方法 `UnsafeArenaSwap()`。此方法既省去了执行 arena 检查的开销，也避免了原本可能发生的复制。

例如，下面的代码在 `Swap()` 调用中会产生一次复制：

```cpp
MyFeatureMessage* message_1 =
  google::protobuf::Arena::Create<MyFeatureMessage>(arena);
message_1->mutable_nested_message()->set_feature_id(11);

MyFeatureMessage* message_2 = new MyFeatureMessage;
message_2->mutable_nested_message()->set_feature_id(22);

message_1->Swap(message_2); // 低效的交换！
```

要避免这段代码中的复制，应把 `message_2` 分配在与 `message_1` 相同的 arena 上：

```cpp
MyFeatureMessage* message_2 =
   google::protobuf::Arena::Create<MyFeatureMessage>(arena);
```

### 粒度 {#granularity}

在大多数应用服务器用例中，我们发现“每请求一个 arena”（arena-per-request）的模型效果良好。你可能想进一步细分 arena 的使用，要么是为了减少堆开销（通过更频繁地销毁较小的 arena），要么是为了缓解表面上的线程竞争问题。然而，使用更细粒度的 arena 可能导致上文所述的意外消息复制。我们还投入了精力针对多线程用例优化 `Arena` 的实现，因此即使某个请求由多个线程处理，在整个请求生命周期内使用单个 arena 也应当是合适的。

## 示例 {#example}

下面是一个简单而完整的示例，演示了 arena 分配 API 的一些特性。

```proto
// my_feature.proto
edition = "2023";

import "nested_message.proto";

package feature_package;

// 下一个可用标签编号：4
message MyFeatureMessage {
  string feature_name = 1;
  repeated int32 feature_data = 2;
  NestedMessage nested_message = 3;
};
```

```proto
// nested_message.proto
edition = "2023";

package feature_package;

// 下一个可用标签编号：2
message NestedMessage {
  int32 feature_id = 1;
};
```

消息的构造与销毁：

```cpp
#include <google/protobuf/arena.h>

Arena arena;

MyFeatureMessage* arena_message =
   google::protobuf::Arena::Create<MyFeatureMessage>(&arena);

arena_message->set_feature_name("Editions Arena");
arena_message->mutable_feature_data()->Add(2);
arena_message->mutable_feature_data()->Add(4);
arena_message->mutable_nested_message()->set_feature_id(247);
```
