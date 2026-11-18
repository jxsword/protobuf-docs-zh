+++
title = "ProtoJSON 格式"
weight = 62
description = "描述 Protobuf 消息的规范化 JSON 表示形式的规范细节。"
type = "docs"
source_url = "https://protobuf.dev/programming-guides/json/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

Protobuf 支持以 JSON 进行规范化（canonical）编码（encoding），从而更容易与不支持标准 Protobuf 二进制线路格式（wire format）的系统共享数据。

本页对该格式作出规定，但还有若干额外的边界情况——它们定义了符合规范的 ProtoJSON 解析器——在 Protobuf 一致性测试套件（Conformance Test Suite）中有所涵盖，此处不逐一详述。

## 格式的非目标 {#non-goals}

### 无法表示某些 JSON 模式 {#non-goals-arbitrary-json-schema}

ProtoJSON 格式的设计定位，是成为可以用 Protobuf 模式（schema）语言表达的那些模式的 JSON 表示形式。

把许多既有的 JSON 模式表示为 Protobuf 模式并用 ProtoJSON 解析，这或许是可行的，但该格式的设计目标并不包括表示任意的 JSON 模式。

例如，Protobuf 模式中没有办法表达那些在 JSON 模式中可能常见的类型写法，比如 `number[][]` 或 `number|string`。

可以使用 `google.protobuf.Struct` 和 `google.protobuf.Value` 类型来让任意 JSON 被解析进 Protobuf 模式，但它们只能把这些值捕获为无模式、无序的键值（key-value）映射。

### 效率不如二进制线路格式 {#non-goals-highly-efficient}

ProtoJSON 格式的效率不如二进制线路格式，而且永远也不会达到。

转换器在编码和解码消息时要消耗更多 CPU，并且（除少数罕见情况外）编码后的消息会占用更多空间。

### 不具备二进制线路格式那样好的模式演进保证 {#non-goals-optimal-schema-evolution}

ProtoJSON 格式不支持未知字段（unknown fields），并且它会把字段名和枚举值名称放进编码后的消息里，这使得日后更改这些名称要困难得多。删除字段是一种破坏性变更（breaking change），会触发解析错误。

更多细节参见下文[JSON 线路安全](#json-wire-safety)。

## 格式描述 {#format}

### 各类型的表示形式 {#field-representation}

下表展示了数据在 JSON 文件中的表示方式。

<table>
  <thead>
    <tr>
      <th>Protobuf 类型</th>
      <th>JSON</th>
      <th>JSON 示例</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>消息（message）</td>
      <td>object</td>
      <td><code>{"fooBar": v, "g": null, ...}</code></td>
      <td>生成 JSON 对象。
        <p>
        键会被序列化（serialization）为字段名（field name）的 lowerCamelCase 形式。关于字段名映射为对象键的更多特殊情况，参见
        <a href="#field-names">字段名</a>。
        <p>
        知名类型（well-known types）有特殊的表示形式，如<a href="#wkt">知名类型表</a>所述。
        <p>
        <code>null</code> 对任何字段都有效，并会让该字段保持未设置。关于 null 值语义行为的澄清，参见<a href="#null-values">null 值</a>。
      </td>
    </tr>
    <tr>
      <td>enum</td>
      <td>string</td>
      <td><code>"FOO_BAR"</code></td>
      <td>使用 proto 中指定的枚举值名称。解析器同时接受枚举名称和整数值。有关带别名的枚举的详情，参见
        <a href="#enum-aliasing">枚举别名</a>。
      </td>
    </tr>
    <tr>
      <td>map&lt;K,V&gt;</td>
      <td>object</td>
      <td><code>{"k": v, ...}</code></td>
      <td>所有键都会被转换为字符串（JSON 中的对象键只能是字符串）。</td>
    </tr>
    <tr>
      <td>repeated V</td>
      <td>array</td>
      <td><code>[v, ...]</code></td>
      <td></td>
    </tr>
    <tr>
      <td>bool</td>
      <td>true, false</td>
      <td><code>true, false</code></td>
      <td></td>
    </tr>
    <tr>
      <td>string</td>
      <td>string</td>
      <td><code>"Hello World!"</code></td>
      <td></td>
    </tr>
    <tr>
      <td>bytes</td>
      <td>base64 string</td>
      <td><code>"YWJjMTIzIT8kKiYoKSctPUB+"</code></td>
      <td>JSON 值将是把数据用带填充（padding）的标准 base64 编码为字符串后的结果。带填充或不带填充的标准或 URL 安全 base64 编码均可接受。
      </td>
    </tr>
    <tr>
      <td>int32, fixed32, uint32</td>
      <td>number</td>
      <td><code>1, -10, 0</code></td>
      <td>JSON 值将是一个数字。数字或字符串均可接受。空字符串无效。指数记法（如 <code>1e2</code>）在带引号与不带引号两种形式下都被接受。
      </td>
    </tr>
    <tr>
      <td>int64, fixed64, uint64</td>
      <td>string</td>
      <td><code>"1", "-10"</code></td>
      <td>JSON 值将是一个十进制字符串。数字或字符串均可接受。空字符串无效。指数记法（如 <code>1e2</code>）在带引号与不带引号两种形式下都被接受。关于 int64 为何使用字符串，参见<a href="#int64-strings">int64 的字符串形式</a>。
      </td>
    </tr>
    <tr>
      <td>float, double</td>
      <td>number</td>
      <td><code>1.1, -10.0, 0, "NaN", "Infinity"</code></td>
      <td>JSON 值将是一个数字，或者是特殊字符串值 "NaN"、"Infinity" 和 "-Infinity" 之一。数字或字符串均可接受。空字符串无效。也接受指数记法。
      </td>
    </tr>
  </tbody>
<table>

<!-- This section html instead of markdown as workaround to bug that escapes all html between the first and last table -->
<h3 id="wkt">知名类型</h3>

<p><code>google.protobuf</code> 包中的某些消息在用 JSON 表示时有特殊的表示形式。

<p><code>google.protobuf</code> 包之外没有任何消息类型有特殊的 ProtoJSON 处理；例如，<code>google.types</code> 包中的类型使用中性表示形式。

<table>
  <thead>
    <tr>
      <th>消息类型</th>
      <th>JSON</th>
      <th>JSON 示例</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Any</td>
      <td><code>object</code></td>
      <td><code>{"@type": "url", "f": v, ... }</code></td>
      <td>参见<a href="#any">Any</a></td>
    </tr>
    <tr>
        <td>Timestamp</td>
        <td>string</td>
        <td><code>"1972-01-01T10:00:20.021Z"</code></td>
        <td>使用 RFC 3339（参见<a href="#rfc3339-timestamp">澄清说明</a>）。生成的输出将始终进行 Z 归一化，带 0、3、6 或 9 位小数部分。也接受 "Z" 以外的时区偏移。
      </td>
    </tr>
    <tr>
      <td>Duration</td>
      <td>string</td>
      <td><code>"1.000340012s", "1s"</code></td>
      <td>生成的输出总是包含 0、3、6 或 9 位小数部分（取决于所需精度），后跟后缀 "s"。只要小数位数适合纳秒精度（也可以没有小数位）且带有必需的后缀 "s"，即可接受。这<b>不是</b> RFC 3339 的 'duration' 格式（参见<a href="#rfc3339-duration">时长</a>的澄清说明）。
      </td>
    </tr>
    <tr>
      <td>Struct</td>
      <td><code>object</code></td>
      <td><code>{ ... }</code></td>
      <td>任意 JSON 对象。参见 <code>struct.proto</code>。</td>
    </tr>
    <tr>
      <td>包装器类型</td>
      <td>various types</td>
      <td><code>2, "2", "foo", true, "true", null, 0, ...</code></td>
      <td>包装器在 JSON 中使用与被包装原始类型相同的表示形式，但 <code>null</code> 在数据转换和传输过程中是允许的，并且会被保留。
      </td>
    </tr>
    <tr>
      <td>FieldMask</td>
      <td>string</td>
      <td><code>"f.fooBar,h"</code></td>
      <td>参见 <code>field_mask.proto</code>。注意，有些字段名无法在 JSON FieldMask 中表示，参见<a href="#fieldmask-limitations">FieldMask 往返限制</a>。</td>
    </tr>
    <tr>
      <td>ListValue</td>
      <td>array</td>
      <td><code>[foo, bar, ...]</code></td>
      <td></td>
    </tr>
    <tr>
      <td>Value</td>
      <td>value</td>
      <td></td>
      <td>任意 JSON 值。详情请查看
        <a href="/reference/protobuf/google.protobuf#value">google.protobuf.Value</a>。
      </td>
    </tr>
    <tr>
      <td>NullValue</td>
      <td>null</td>
      <td></td>
      <td>JSON null。<a href="#null-values">null 解析行为</a>的特殊情形。</td>
    </tr>
    <tr>
      <td>Empty</td>
      <td>object</td>
      <td><code>{}</code> <b>（未作特殊处理）</b></td>
      <td>一个空的 JSON 对象</td>
    </tr>
  </tbody>
</table>

### 字段名作为 JSON 键 {#field-names}

消息字段名会被映射为 lowerCamelCase，用作 JSON 对象键。如果指定了 `json_name` 字段选项，则改用指定的值作为键。

解析器同时接受 lowerCamelCase 名称（或 `json_name` 选项指定的名称）与原始 proto 字段名。这使得序列化器可以选择使用原始字段名进行打印（参见 [JSON 选项](#json-options)），而得到的输出仍能被所有符合规范的解析器解析回来。

`json_name` 的值中不允许出现 `\0 (nul)`。原因详见<a href="/news/2023-04-28#json-name">json_name 的更严格校验</a>。注意，`\0` 仍被视为 `string` 字段取值中的合法字符。

### 字段存在性与默认值 {#presence}

从 Protobuf 消息生成 JSON 编码输出时，如果字段支持存在性，序列化器必须当且仅当相应的 hazzer 会返回 true 时输出该字段的值。

如果字段不支持字段存在性（field presence）且具有默认值（default value）（例如任何空的 repeated 字段），序列化器应将其从输出中省略。实现可以提供选项，把带有默认值的字段包含进输出。

### null 值 {#null-values}

序列化器不应输出 `null` 值。

解析器接受 `null` 作为任何字段的合法值，其行为如下：

*   键有效性检查仍应照常进行，不允许未知字段。
*   该字段应保持未设置，就像它完全不存在于输入中一样（在适用的场合，hazzer 仍应返回 false）。

这意味着，对隐式存在性（implicit presence）字段给出 `null` 值时，其行为与该字段取默认值时的行为完全相同，因为这些字段没有 hazzer。例如，对 repeated 字段给出 `null` 或 `[]` 值会触发键有效性检查，但除此之外，两者的表现都与 JSON 中完全不存在该字段时一样。

repeated 字段内部不允许出现 `null` 值。

`google.protobuf.NullValue` 是这一行为的一个特殊例外：对这个类型，`null` 会被当作“哨兵式已设置”的值来处理，因此这种类型的字段必须由序列化器和解析器按照标准存在性行为来处理。相应地，这一行为也让 `google.protobuf.Struct` 和 `google.protobuf.Value` 能够无损地往返（round trip）任意 JSON。

### 重复键 {#duplicate-keys}

ProtoJSON 构建在 JSON 之上。遗憾的是，对于同一个 JSON 对象中出现重复键的情形，JSON 并没有确立一致的行为。例如，[RFC 8259](https://datatracker.ietf.org/doc/html/rfc8259#section-4) 指出 JSON 对象内的名称 SHOULD（应当）唯一，但也指出当名称不唯一时各实现行为各异。有些解析器会直接失败，但大多数采用“后者胜出”（last-wins）语义（与浏览器的行为一致）。此外，JSON 解析器可能保留、也可能不保留原始的键顺序信息。

ProtoJSON 带来了额外的复杂性，因为重复字段不仅可能来自逐字相同的键，还可能来自：

*   同一字段名的不同拼写（例如 `camelCase` 与 `snake_case`）。
*   属于同一个 `oneof` 的两个不同字段。

为消除这些歧义，ProtoJSON 定义了以下行为：

*   **序列化器**：符合规范的 ProtoJSON 序列化器**绝不得（MUST NOT）**输出重复键（包括同一 `oneof` 内的多个字段）。
*   **解析器**：
    *   在所有可能的情况下都应采用“后者胜出”行为。
        *   当实现构建在一个表现出“后键胜出”（last-key-wins）行为的现成 JSON 解析器之上时，这是自然的结果。
        *   如果使用的 JSON 解析器能够保留原始字段顺序，那么键的不同拼写以及同一 oneof 内的两个不同字段也应采用“后者胜出”。
    *   凡是在实现“后者胜出”不切实际的地方，解析都必须失败，而不能任意挑选一个胜出。
        *   常见情形是：ProtoJSON 解析器构建在一个对完全相同的键实现“后者胜出”、但不在结果对象中维护顺序的 JSON 解析器之上；此时，对完全重复的键应采用“后者胜出”，而对重复的不同拼写或同一 oneof 内的两个字段则应解析失败。

任何其他行为（包括“先者胜出”“任意一个胜出”或合并字段）都不应使用。不过，由于底层 JSON 规范认为一系列行为都是可允许的，强烈建议系统避免依赖 ProtoJSON 对重复键的任何特定处理方式。

### 超出范围的数值 {#out-of-range-values}

解析数值时，如果从线路解析出的数字不适合对应类型，解析器应解析失败。

这包括 `uint32` 的任何负数，以及 `int32` 中小于 `INT_MIN` 或大于 `INT_MAX` 的数字。

整数类型字段不允许带有非零小数部分的值。小数部分为零的值可以接受。例如，`1.0` 对 int32 字段有效，而 `1.5` 则无效。

### int64 的字符串形式 {#int64-strings}

遗憾的是，[json.org](https://json.org) 规范并未提及数字的预期精度上限。许多实现遵循 JSON 所源自的原始 JS 行为，把所有数字都解释为 binary64（双精度），当数字是大于 2**53 的整数时会静默丢失精度。其他实现可能支持无限精度的 bigint、int64，甚至支持小数部分精度无限的 bigfloat。

这就造成了一种局面：如果 JSON 中包含一个无法用双精度精确表示的数字，不同解析器的行为会各不相同，包括在许多语言中静默丢失精度。

为避免这些问题，ProtoJSON 序列化器把 int64 以字符串形式输出，确保任何实现处理大 int64 时都不会发生精度损失。

在期望 int64 却解析到一个裸数字时，即使相应语言内置的 JSON 解析器支持把 JSON 数字解析为 bigint，实现也应把该值强制转换为双精度。这可以确保同一份数据无论使用哪种语言都得到一致的解读。

这一设计遵循了在优先考虑互操作性时如何处理 JSON 大数字的既定最佳实践，包括：

*   [RFC8259](https://datatracker.ietf.org/doc/html/rfc8259#section-6) 包含一条说明：希望获得良好互操作性的软件应只把所有数字都假定为双精度。

*   [OpenAPI int64](https://spec.openapis.org/registry/format/int64) 文档建议，在需要超出 2**53 的精度时，使用 JSON 字符串而非数字。

## 枚举别名 {#enum-aliasing}

当枚举定义带有 `option allow_aliasing = true;` 时，多个枚举常量名可以映射到同一个数值。

### 序列化行为

序列化器**必须**为给定数值打印枚举定义中列出的第一个名称。

例如，给定：

```proto
enum MyEnum {
  option allow_alias = true;
  UNKNOWN = 0;
  OLD_NAME = 1;
  NEW_NAME = 1;
}
```

如果值是 `1`，序列化器会输出 `"OLD_NAME"`。

### 解析行为

解析器**必须**接受为该数值定义的任何名称。在上面的示例中，解析器会把 `"OLD_NAME"` 和 `"NEW_NAME"` 都接受为映射到值 `1`。

### 安全的重命名策略 {#safe-renaming}

这一行为为在分布式系统中重命名枚举值提供了一条安全的多步迁移路径：

1.  **将新名称添加为别名：**把新名称添加到旧名称之下，映射到相同的值。

    ```proto
    enum MyEnum {
      option allow_aliasing = true;
      UNKNOWN = 0;
      OLD_NAME = 1;
      NEW_NAME = 1; // 新名称作为别名添加
    }
    ```

2.  **部署模式：**把这份模式部署到所有系统。此时，所有解析器都会识别 `OLD_NAME` 和 `NEW_NAME`，但所有序列化器仍会输出 `OLD_NAME`（因为它列在前面）。

3.  **交换顺序：**交换 proto 文件中各别名的顺序。

    ```proto
    enum MyEnum {
      option allow_aliasing = true;
      UNKNOWN = 0;
      NEW_NAME = 1; // 新名称现在排在最前
      OLD_NAME = 1;
    }
    ```

4.  **部署模式：**部署这份更新后的模式。现在，序列化器将开始输出 `NEW_NAME`。解析器仍会接受两个名称，从而确保仍在运行上一版模式的任何系统都能安全解析新名称。

5.  **移除旧名称：**一旦所有系统都已完成更新，并且你确信不再有需要由可能被回滚的系统来解析的旧序列化数据，就可以安全地移除旧名称。

    ```proto
    enum MyEnum {
      UNKNOWN = 0;
      NEW_NAME = 1;
    }
    ```

出于同样的原因，这一语义也与 TextProto 相符。

## Any {#any}

### 普通消息 {#any-normal-messages}

如果某条消息不是具有特殊 JSON 表示形式的知名类型，那么 `Any` 内包含的这条消息会被转换成一个 JSON 对象，并额外插入一个 `"@type"` 字段，其中包含设置在该 `Any` 上的 `type_url`。

例如，如果你有如下消息定义：

```proto
package x;
message Child { int32 x = 1; string y = 2; }
```

当 Child 的一个实例被打包进 `Any` 时，其 JSON 表示形式为：

```json
{
  "@type": "type.googleapis.com/x.Child",
  "x": 1,
  "y": "hello world"
}
```

### 特殊处理的知名类型 {#any-special-cases}

如果 `Any` 中包含具有特殊 JSON 映射（JSON mapping）的知名类型，该消息会被转换为特殊表示形式，并被设置为一个键为 "value" 的字段。

例如，表示 3.1 秒的 `google.protobuf.Duration` 在特殊情形处理中会用字符串 `"3.1s"` 来表示。当该 `Duration` 被打包进 `Any` 时，它将被序列化为：

```json
{
  "@type": "type.googleapis.com/google.protobuf.Duration",
  "value": "3.1s"
}
```

具有特殊 JSON 编码的消息类型包括：

-   `google.protobuf.Any`
-   `google.protobuf.BoolValue`
-   `google.protobuf.BytesValue`
-   `google.protobuf.DoubleValue`
-   `google.protobuf.Duration`
-   `google.protobuf.FieldMask`
-   `google.protobuf.FloatValue`
-   `google.protobuf.Int32Value`
-   `google.protobuf.Int64Value`
-   `google.protobuf.ListValue`
-   `google.protobuf.StringValue`
-   `google.protobuf.Struct`
-   `google.protobuf.Timestamp`
-   `google.protobuf.UInt32Value`
-   `google.protobuf.UInt64Value`
-   `google.protobuf.Value`

注意，`google.protobuf.Empty` 不被认为具有任何特殊的 JSON 映射；它只是一个没有任何字段的普通消息。这意味着，被打包进 `Any` 的 `Empty` 的预期表示形式是 `{"@type": "type.googleapis.com/google.protobuf.Empty"}`，而不是 `{"@type": "type.googleapis.com/google.protobuf.Empty", "value": {}}`。

## ProtoJSON 线路安全 {#json-wire-safety}

使用 ProtoJSON 时，在分布式系统中只有部分模式变更可以安全进行。这与应用于[二进制线路格式](/programming-guides/editions#updating)的相同概念形成了对比。

### JSON 线路不安全变更 {#wire-unsafe}

线路不安全变更指的是这样的模式变更：如果你用采用新模式的解析器去解析以旧模式序列化的数据（或反过来），就会出现破坏。你几乎永远都不应做这类模式变更。

*   把字段改成具有相同编号和类型的扩展（extension），或从这样的扩展改回来，是不安全的。
*   在 `string` 与 `bytes` 之间变更字段是不安全的。
*   在消息类型与 `bytes` 之间变更字段是不安全的。
*   把任何字段从 `optional` 改为 `repeated` 是不安全的。
*   在 `map<K, V>` 与对应的 `repeated` 消息字段之间变更字段是不安全的。
*   把字段移入现有的 `oneof` 是不安全的。

### JSON 线路安全变更 {#wire-safe}

线路安全变更指的是：以这种方式演进模式是完全安全的，不会有数据丢失或新增解析失败的风险。

注意，几乎所有线路安全变更对应用代码而言都可能是破坏性变更。例如，向既有枚举添加一个值，对任何对该枚举写了穷尽式 switch 的代码来说都是编译层面的破坏。因此，Google 可能会避免对公开消息进行其中某些类型的变更。AIP 中包含关于其中哪些变更可以安全进行的指引。

*   把单个 `optional` 字段改为**新** `oneof` 的成员是安全的。
*   把只包含一个字段的 `oneof` 改为 `optional` 字段是安全的。
*   在 `int32`、`sint32`、`sfixed32`、`fixed32` 任意之间变更字段是安全的。
*   在 `int64`、`sint64`、`sfixed64`、`fixed64` 任意之间变更字段是安全的。
*   变更字段编号是安全的（因为 ProtoJSON 格式不使用字段编号），但仍强烈不建议这样做，因为它在二进制线路格式中非常不安全。
*   如果在所有相关客户端上都设置了“把枚举值输出为整数”，则向枚举添加值是安全的（参见[选项](#json-options)）

### JSON 线路兼容变更（有条件安全） {#conditionally-safe}

与线路安全变更不同，线路兼容意味着同一份数据在给定变更前后都能被解析。但是，在这种形式的变更下，读取数据的客户端会得到有损的数据。例如，把 int32 改为 int64 是兼容变更，但如果写入了大于 INT32_MAX 的值，以 int32 读取它的客户端会丢弃高位。

只有谨慎管理向你的系统推广上线的过程，你才能对模式进行兼容变更。例如，你可以把 int32 改为 int64，但要确保在新模式部署到所有端点之前，一直只写入合法的 int32 值，然后再开始写入更大的值。

#### 兼容但存在未知字段处理问题 {#compatible-ish}

与二进制线路格式不同，ProtoJSON 实现通常不会传播未知字段。这意味着，向模式添加内容通常是兼容的，但如果使用旧模式的客户端看到新内容，就会导致解析失败。

这意味着你可以向模式添加内容，但在确认模式已部署到相关客户端或服务器之前（或相关客户端设置了“忽略未知字段”标志，参见[下文](#json-options)），你不能安全地开始写入这些内容。

*   在此前提下，添加和删除字段被视为兼容。
*   在此前提下，删除枚举值被视为兼容。

#### 兼容但可能有损 {#compatible-lossy}

*   在 32 位整数（`int32`、`uint32`、`sint32`、`sfixed32`、`fixed32`）与 64 位整数（`int64`、`uint64`、`sint64`、`sfixed32`）任意两者之间变更都是兼容变更。
    *   如果从线路解析出的数字不适合对应类型，就会发生解析失败。
    *   与二进制线路格式不同，`bool` 与整数类型不兼容。
    *   注意，int64 和 uint64 类型默认带引号，以避免在按 double 或 JavaScript 数字处理时丢失精度；而 32 位类型默认不带引号。符合规范的解析器对所有整数类型都会接受带引号或不带引号两种形式，但不符合规范的实现可能错误处理这种情况，不支持带引号的 int32 或不带引号的 int64，因此须多加小心。
*   `enum` 可能与 `string` 有条件地兼容
    *   如果有任何客户端使用了"enums-as-ints"标志，枚举就会改为与整数类型兼容。

## RFC 3339 澄清说明 {#rfc3339}

### 时间戳 {#rfc3339-timestamp}

ProtoJSON 时间戳使用 RFC 3339 时间戳格式。遗憾的是，RFC 3339 规范中的某些含糊之处造成了一些边界情况，使得其他各种 RFC 3339 实现对这种格式是否合法看法不一。

[RFC 3339](https://www.rfc-editor.org/rfc/rfc3339) 意在声明 ISO-8601 格式的一个严格子集；而 RFC 3339 于 2002 年发布后，ISO-8601 随后经过了修订，RFC 3339 却没有任何相应修订，由此又产生了一些额外的含糊之处。

最值得注意的是，ISO-8601-1988 包含这样一条注记：

> 在日期和时间的表示中，当大写字符不可用时，可以使用小写字符。

这条注记究竟是在说解析器一般都应接受小写字母，还是只是说在技术上无法使用大写字母的环境中可以用小写字母代替，并不明确。RFC 3339 中包含一条注记，意图把解读澄清为：一般应接受小写字母。

ISO-8601-2019 不包含对应的注记，并且明确表示不允许使用小写字母。

这给所有声明支持 RFC 3339 的库造成了一些困惑：如今 RFC 3339 声明自己是 ISO-8601 的一个子集规范（profile），但其包含的一条澄清性注记所引用的文本，在最新的 ISO-8601 规范中并不存在。

ProtoJSON 规范决定采用更严格的定义，即“作为 ISO-8601-2019 子集规范的 RFC 3339”。某些 Protobuf 实现可能不符合规范：它们使用按“作为 ISO-8601-1988 子集规范的 RFC 3339”实现的时间戳解析，这会额外接受少数几种边界情况。

为了获得一致的互操作性，解析器应尽可能只接受更严格的子集格式。在使用接受更宽松定义的不符合规范的实现时，务必极力避免依赖那些被额外接受的边界情况。

### 时长 {#rfc3339-duration}

RFC 3339 还定义了一种时长（duration）格式，但遗憾的是，RFC 3339 时长格式没有任何表达亚秒级分辨率的方式。

ProtoJSON 的时长编码直接借鉴了 RFC 3339 的 `dur-seconds` 表示法，但它能够编码纳秒级精度。当秒数为整数时，两种表示可能一致（例如 `10s`），但 ProtoJSON 时长接受小数值，且符合规范的实现必须精确表示纳秒级精度（例如 `10.500000001s`）。

## 知名类型不可往返的边界情况 {#wkt-roundtrip-limitations}

尽管 ProtoJSON 为所有 Protobuf 类型定义了规范化的 JSON 表示，但由于该格式自身的设计缺陷，在某些边界情况下，知名类型无法干净地完成往返，即无法把 JSON 反序列化（deserialization）回 proto，也无法反向操作。

例如，`google.protobuf.Value` 用一个 double 字段来表示 JSON 数字。JSON 数字可以表示除 `Infinity`、`-Infinity` 和 `NaN` 之外的任何 double；如果在构造 `Value` 消息时设置了这三个值，得到的消息将无法通过 JSON 格式往返。

这些边界情况很罕见。一旦发生，实现可能序列化失败，也可能序列化出无法解析回与原值完全相同内容的结果。

### 无法往返的 FieldMask {#fieldmask-limitations}

最重要的往返限制之一是：JSON 表示中的 `google.protobuf.FieldMask` 无法用来表示那些无法在 `snake_case` 与 `camelCase` 之间无损转换的字段名。

在 JSON 中表示 `FieldMask` 时，原始字段名会从 `snake_case` 转换为 `lowerCamelCase`。把 JSON `FieldMask` 解析回来时，解析器必须把 camelCase 路径段转回 snake_case。

然而，与 camelCase 相互往返并不是无损的。例如：

*   **包含“下划线后跟数字”的字段名**（例如 `x_0`、`custom_label_0`）：`x_0` 的 camelCase 表示是 `x0`。把 `x0` 转回 snake_case 时仍然是 `x0`，无法恢复下划线。
*   **带连续下划线或前导/末尾下划线的字段名**（例如 `_x`、`__foo_bar`、`foo__bar`）：大小写与还原规则无法把它们与标准 camelCase 区分开。

处理标准字段时，可以通过查看具体模式中的字段定义来寻找匹配，从而消解歧义。但由于 `FieldMask` 路径在解析期间不会与任何具体消息类型相关联，转换步骤无法参考模式。这意味着某些字段名无法往返表示。

为避免这些问题，请遵循标准 Protobuf 样式指南（style guide），避免使用下划线后跟数字，以及连续/前导/末尾下划线。从版次 2024（Edition 2024）开始，为防止出现问题，`protoc` 会拒绝这些命名模式。

## JSON 选项 {#json-options}

符合规范的 Protobuf JSON 实现可以提供以下选项：

*   **始终输出无存在性的字段**：不支持存在性且具有默认值的字段默认会在 JSON 输出中被省略（例如取值为 0 的隐式存在性整数、取值为空字符串的隐式存在性字符串字段，以及空的 repeated 字段和 map 字段）。实现可以提供选项来覆盖这一行为，改为输出带有默认值的字段。

    自 v25.x 起，C++、Java 和 Python 实现不符合规范，因为这个标志影响 proto2 `optional` 字段，却不影响 proto3 `optional` 字段。计划在未来的发布（release）中修复。

*   **忽略未知字段**：Protobuf JSON 解析器默认应拒绝未知字段，但可以提供在解析时忽略未知字段的选项。

*   **使用 proto 字段名而非 lowerCamelCase 名称**：默认情况下，Protobuf JSON 打印器应把字段名转换为 lowerCamelCase 并将其用作 JSON 名称。实现可以提供选项改用 proto 字段名作为 JSON 名称。Protobuf JSON 解析器必须同时接受转换后的 lowerCamelCase 名称和 proto 字段名。

*   **把枚举值输出为整数而非字符串**：JSON 输出中默认使用枚举值的名称。可以提供选项改为使用枚举值的数值。
