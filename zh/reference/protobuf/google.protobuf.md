+++
title = "Protobuf 知名类型"
weight = 830
linkTitle = "知名类型"
description = "google.protobuf 包的 API 文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/protobuf/google.protobuf/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-19"
status = "translated"
translator = "agent"
+++

## 索引

-   [`Any`](#any)（消息）
-   [`Api`](#api)（消息）
-   [`BoolValue`](#bool-value)（消息）
-   [`BytesValue`](#bytes-value)（消息）
-   [`DoubleValue`](#double-value)（消息）
-   [`Duration`](#duration)（消息）
-   [`Empty`](#empty)（消息）
-   [`Enum`](#enum)（消息）
-   [`EnumValue`](#enum-value)（消息）
-   [`Field`](#field)（消息）
-   [`Field.Cardinality`](#field-cardinality)（枚举）
-   [`Field.Kind`](#field-kind)（枚举）
-   [`FieldMask`](#field-mask)（消息）
-   [`FloatValue`](#float-value)（消息）
-   [`Int32Value`](#int32-value)（消息）
-   [`Int64Value`](#int64-value)（消息）
-   [`ListValue`](#list-value)（消息）
-   [`Method`](#method)（消息）
-   [`Mixin`](#mixin)（消息）
-   [`NullValue`](#null-value)（枚举）
-   [`Option`](#option)（消息）
-   [`SourceContext`](#source-context)（消息）
-   [`StringValue`](#string-value)（消息）
-   [`Struct`](#struct)（消息）
-   [`Syntax`](#syntax)（枚举）
-   [`Timestamp`](#timestamp)（消息）
-   [`Type`](#type)（消息）
-   [`UInt32Value`](#uint32-value)（消息）
-   [`UInt64Value`](#uint64-value)（消息）
-   [`Value`](#value)（消息）

以 "`Value`" 结尾的知名类型（well-known types）是其他类型的包装消息（message），
例如 `BoolValue` 和 `EnumValue`。它们现已过时。如今仍要使用包装器（wrapper）的理由只有：

*   与已在使用这些包装器的消息保持线路兼容。
*   如果你想将一个标量（scalar）值（value）放入 `Any` 消息中。

在大多数情况下，有更好的选择：

*   对于新消息，更好的做法是使用常规的显式存在性（explicit presence）字段（field）
    （proto2/proto3 中为 `optional`，版次（edition）>= 2023 中为常规字段）。
*   [扩展（extension）通常是比 `Any` 字段更好的选项（option）](/design-decisions/extensions-over-any)。

## Any {#any}

`Any` 包含一条任意序列化后的消息，以及一个描述该已序列化消息类型的 URL。

#### JSON {#json}

`Any` 值的 JSON 表示形式使用反序列化后内嵌消息的常规表示形式，外加一个包含类型 URL 的
附加字段 `@type`。示例：

```proto
package google.profile;
message Person {
  string first_name = 1;
  string last_name = 2;
}
```

```json
{
  "@type": "type.googleapis.com/google.profile.Person",
  "firstName": <string>,
  "lastName": <string>
}
```

如果内嵌消息类型是知名类型且拥有自定义 JSON 表示形式，则该表示形式会被内嵌进来：在
`@type` 字段之外，再添加一个承载该自定义 JSON 的 `value` 字段。示例（消息
`google.protobuf.Duration`）：

```json
{
  "@type": "type.googleapis.com/google.protobuf.Duration",
  "value": "1.212s"
}
```

<table id="google.protobuf.Any.FIELDS">
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>type_url</code></td>
      <td><code class="apitype">string</code></td>
      <td><p>一个 URL 或资源名称，其内容描述了已序列化消息的类型。</p><p>对于使用 <code>http</code>、<code>https</code> 模式（schema）或不使用模式的 URL，适用以下限制和解释：</p>
<ul>
  <li>如果未提供模式，则默认采用 <code>https</code>。</li>
  <li>URL 路径的最后一段必须表示该类型的完全限定（fully-qualified）名称（如 <code>path/google.protobuf.Duration</code>）。</li>
  <li>对该 URL 发起 HTTP GET 必须返回二进制格式（binary format）的 <code><a href="#type">google.protobuf.Type</a></code> 值，否则产生错误。</li>
  <li>允许应用程序基于该 URL 缓存查找结果，或将其预编译进二进制文件以避免任何查找。因此，类型变更时需要保持二进制兼容性。（使用带版本号的类型名称来管理破坏性变更（breaking change）。）</li>
</ul><p><code>http</code>、<code>https</code>（或空模式）以外的模式可能与实现特定的语义一同使用。</p></td>
    </tr>
    <tr>
      <td><code>value</code></td>
      <td><code class="apitype">bytes</code></td>
      <td>必须是上述指定类型的有效序列化数据。</td>
    </tr>
  </tbody>
</table>

## Api {#api}

Api 是 Protobuf 服务（service）的轻量级描述符（descriptor）。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>name</code></td>
      <td><code>string</code></td>
      <td>
        此 api 的完全限定名称，包含 package 名称，后接该 api 的简单名称。
      </td>
    </tr>
    <tr>
      <td><code>methods</code></td>
      <td>
        <code><a href="#method">Method</a></code>
      </td>
      <td>此 api 的各方法，顺序未作规定。</td>
    </tr>
    <tr>
      <td><code>options</code></td>
      <td>
<code><a href="#option">Option</a></code>
      </td>
      <td>附加到该 API 的任意元数据。</td>
    </tr>
    <tr>
      <td>版本（<code>version</code>）</td>
      <td><code>string</code></td>
      <td>
        <p>
          此 api 的版本字符串。如果指定，必须采用
          <code>major-version.minor-version</code> 的形式，例如 <code>1.10</code>。
          如果省略次版本号，则默认为零。如果整个版本字段为空，则主版本号将从
          package 名称推导而来，如下文所述。如果该字段不为空，package 名称中的版本
          将被校验是否与此处提供的内容一致。
        </p>
        <p>
          版本管理架构采用
          <a href="http://semver.org">语义化版本</a>：主版本号表示破坏性变更，
          次版本号表示附加性的、非破坏性变更。这两个版本号向用户传递了对不同版本
          应有的预期，应根据产品计划审慎选择。
        </p>
        <p>
          主版本号也会体现在 API 的 package 名称中，package 名称必须以
          <code>v&lt;major-version&gt;</code> 结尾，例如
          <code>google.feature.v1</code>。主版本 0 和 1 可以省略该后缀。
          主版本号 0 只能用于实验性的、未正式发布（GA）的 api。
        </p>
      </td>
    </tr>
    <tr>
      <td><code>source_context</code></td>
      <td>
        <code
          ><code
            ><a href="#source-context">SourceContext</a></code
          ></code
        >
      </td>
      <td>
        此消息所表示的 Protobuf 服务的源上下文。
      </td>
    </tr>
    <tr>
      <td><code>mixins</code></td>
      <td>
        <code
          ><code><a href="#mixin">Mixin</a></code></code
        >
      </td>
      <td>
        被包含的 API。参见
        <code><a href="#mixin">Mixin</a></code>。
      </td>
    </tr>
    <tr>
      <td><code>syntax</code></td>
      <td>
        <code><a href="#syntax">Syntax</a></code>
      </td>
      <td>该服务的源语法。</td>
    </tr>
  </tbody>
</table>

## BoolValue {#bool-value}

`bool` 的包装消息。

`BoolValue` 的 JSON 表示形式是 JSON `true` 和 `false`。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code class="apitype">bool</code></td>
      <td>bool 值。</td>
    </tr>
  </tbody>
</table>

## BytesValue {#bytes-value}

`bytes` 的包装消息。

`BytesValue` 的 JSON 表示形式是 JSON 字符串。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code>bytes</code></td>
      <td>bytes 值。</td>
    </tr>
  </tbody>
</table>

## DoubleValue {#double-value}

`double` 的包装消息。

`DoubleValue` 的 JSON 表示形式是 JSON 数字。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code>double</code></td>
      <td>double 值。</td>
    </tr>
  </tbody>
</table>

## Duration {#duration}

Duration 表示一段有符号的、固定长度的时间跨度，以秒数和纳秒分辨率的秒的小数部分表示。
它独立于任何日历以及“天”或“月”等概念。它与 Timestamp 的关系在于：两个 Timestamp 值之差
是一个 Duration，并且 Duration 可以与 Timestamp 相加或相减。范围约为 ±10,000 年。

示例 1：用伪代码从两个 Timestamp 计算 Duration。

```c
Timestamp start = ...;
Timestamp end = ...;
Duration duration = ...;

duration.seconds = end.seconds - start.seconds;
duration.nanos = end.nanos - start.nanos;

if (duration.seconds < 0 && duration.nanos > 0) {
  duration.seconds += 1;
  duration.nanos -= 1000000000;
} else if (duration.seconds > 0 && duration.nanos < 0) {
  duration.seconds -= 1;
  duration.nanos += 1000000000;
}
```

示例 2：用伪代码从 Timestamp + Duration 计算 Timestamp。

```c
Timestamp start = ...;
Duration duration = ...;
Timestamp end = ...;

end.seconds = start.seconds + duration.seconds;
end.nanos = start.nanos + duration.nanos;

if (end.nanos < 0) {
  end.seconds -= 1;
  end.nanos += 1000000000;
} else if (end.nanos >= 1000000000) {
  end.seconds += 1;
  end.nanos -= 1000000000;
}
```

`Duration` 的 JSON 表示形式是一个以 `s` 结尾（表示秒）的 `String`，前面是秒数，
纳秒以秒的小数部分表示。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>seconds</code></td>
      <td><code>int64</code></td>
      <td>
        时间跨度的带符号秒数。必须介于 -315,576,000,000 到
        +315,576,000,000 之间（含边界）。
      </td>
    </tr>
    <tr>
      <td><code>nanos</code></td>
      <td><code>int32</code></td>
      <td>
        时间跨度在纳秒分辨率下的带符号秒的小数部分。小于一秒的 Duration 用值为 0 的
        <code>seconds</code> 字段和正或负的 <code>nanos</code> 字段表示。对于大于等于
        一秒的 Duration，<code>nanos</code> 字段的非零值必须与 <code>seconds</code>
        字段同号。必须介于 -999,999,999 到
        +999,999,999 之间（含边界）。
      </td>
    </tr>
  </tbody>
</table>

## Empty {#empty}

一个通用的空消息，你可以复用它，以避免在自己的 API 中定义重复的空消息。一个典型的
用法是将其用作 API 方法的请求或响应类型。例如：

```proto
service Foo {
  rpc Bar(google.protobuf.Empty) returns (google.protobuf.Empty);
}
```

`Empty` 的 JSON 表示形式是空 JSON 对象 `{}`。

## Enum {#enum}

枚举类型定义

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>name</code></td>
      <td><code>string</code></td>
      <td>枚举类型名称。</td>
    </tr>
    <tr>
      <td><code>enumvalue</code></td>
      <td>
        <code><a href="#enum-value">EnumValue</a></code>
      </td>
      <td>枚举值定义。</td>
    </tr>
    <tr>
      <td><code>options</code></td>
      <td>
        <code><a href="#option">Option</a></code>
      </td>
      <td>Protobuf 选项。</td>
    </tr>
    <tr>
      <td><code>source_context</code></td>
      <td>
        <code><a href="#source-context">SourceContext</a></code>
      </td>
      <td>源上下文。</td>
    </tr>
    <tr>
      <td><code>syntax</code></td>
      <td>
        <code><a href="#syntax">Syntax</a></code>
      </td>
      <td>源语法。</td>
    </tr>
    <tr>
      <td><code>edition</code></td>
      <td><code>string</code>
      </td>
      <td>如果 <code>syntax</code> 为 <code>SYNTAX_EDITIONS</code>，则为源版次。</td>
    </tr>
  </tbody>
</table>

## EnumValue {#enum-value}

枚举值定义。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>name</code></td>
      <td><code>string</code></td>
      <td>枚举值名称。</td>
    </tr>
    <tr>
      <td><code>number</code></td>
      <td><code>int32</code></td>
      <td>枚举值编号。</td>
    </tr>
    <tr>
      <td><code>options</code></td>
      <td>
        <code><a href="#option">Option</a></code>
      </td>
      <td>Protobuf 选项。</td>
    </tr>
  </tbody>
</table>

## Field {#field}

消息类型中的单个字段。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>kind</code></td>
      <td>
        <code><a href="#field-kind">Kind</a></code>
      </td>
      <td>字段类型。</td>
    </tr>
    <tr>
      <td>基数（<code>cardinality</code>）</td>
      <td>
        <code><a href="#field-cardinality">Cardinality</a></code>
      </td>
      <td>字段的基数（cardinality）。</td>
    </tr>
    <tr>
      <td><code>number</code></td>
      <td><code>int32</code></td>
      <td>字段编号。</td>
    </tr>
    <tr>
      <td><code>name</code></td>
      <td><code>string</code></td>
      <td>字段名。</td>
    </tr>
    <tr>
      <td><code>type_url</code></td>
      <td><code>string</code></td>
      <td>
        消息或枚举类型的字段类型 URL（不含模式（scheme）部分）。示例：
        <code>&quot;type.googleapis.com/google.protobuf.Timestamp&quot;</code>。
      </td>
    </tr>
    <tr>
      <td><code>oneof_index</code></td>
      <td><code>int32</code></td>
      <td>
        对于消息或枚举类型，为该字段类型在 <code>Type.oneofs</code> 中的索引。
        第一个类型的索引为 1；0 表示该类型不在列表中。
      </td>
    </tr>
    <tr>
      <td><code>packed</code></td>
      <td><code>bool</code></td>
      <td>是否使用替代的 packed 线路表示形式。</td>
    </tr>
    <tr>
      <td><code>options</code></td>
      <td>
        <code><a href="#option">Option</a></code>
      </td>
      <td>Protobuf 选项。</td>
    </tr>
    <tr>
      <td><code>json_name</code></td>
      <td><code>string</code></td>
      <td>字段的 JSON 名称。</td>
    </tr>
    <tr>
      <td><code>default_value</code></td>
      <td><code>string</code></td>
      <td>
        此字段默认值（default value）的字符串值。仅限 proto2 语法。
      </td>
    </tr>
  </tbody>
</table>

## Cardinality {#field-cardinality}

字段是 optional、required 还是 repeated。

<table>
  <thead>
    <tr>
      <th>枚举值</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>CARDINALITY_UNKNOWN</code></td>
      <td>用于基数未知的字段。</td>
    </tr>
    <tr>
      <td><code>CARDINALITY_OPTIONAL</code></td>
      <td>用于 optional 字段。</td>
    </tr>
    <tr>
      <td><code>CARDINALITY_REQUIRED</code></td>
      <td>用于 required 字段。仅限 proto2 语法。</td>
    </tr>
    <tr>
      <td><code>CARDINALITY_REPEATED</code></td>
      <td>用于 repeated 字段。</td>
    </tr>
  </tbody>
</table>

## Kind {#field-kind}

基本字段类型。

<table class="matchpre">
  <thead>
    <tr>
      <th>枚举值</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>TYPE_UNKNOWN</code></td>
      <td>字段类型 unknown。</td>
    </tr>
    <tr>
      <td><code>TYPE_DOUBLE</code></td>
      <td>字段类型 double。</td>
    </tr>
    <tr>
      <td><code>TYPE_FLOAT</code></td>
      <td>字段类型 float。</td>
    </tr>
    <tr>
      <td><code>TYPE_INT64</code></td>
      <td>字段类型 int64。</td>
    </tr>
    <tr>
      <td><code>TYPE_UINT64</code></td>
      <td>字段类型 uint64。</td>
    </tr>
    <tr>
      <td><code>TYPE_INT32</code></td>
      <td>字段类型 int32。</td>
    </tr>
    <tr>
      <td><code>TYPE_FIXED64</code></td>
      <td>字段类型 fixed64。</td>
    </tr>
    <tr>
      <td><code>TYPE_FIXED32</code></td>
      <td>字段类型 fixed32。</td>
    </tr>
    <tr>
      <td><code>TYPE_BOOL</code></td>
      <td>字段类型 bool。</td>
    </tr>
    <tr>
      <td><code>TYPE_STRING</code></td>
      <td>字段类型 string。</td>
    </tr>
    <tr>
      <td><code>TYPE_GROUP</code></td>
      <td>字段类型为组（group）。仅限 proto2 语法，且已弃用。</td>
    </tr>
    <tr>
      <td><code>TYPE_MESSAGE</code></td>
      <td>字段类型 message。</td>
    </tr>
    <tr>
      <td><code>TYPE_BYTES</code></td>
      <td>字段类型 bytes。</td>
    </tr>
    <tr>
      <td><code>TYPE_UINT32</code></td>
      <td>字段类型 uint32。</td>
    </tr>
    <tr>
      <td><code>TYPE_ENUM</code></td>
      <td>字段类型 enum。</td>
    </tr>
    <tr>
      <td><code>TYPE_SFIXED32</code></td>
      <td>字段类型 sfixed32。</td>
    </tr>
    <tr>
      <td><code>TYPE_SFIXED64</code></td>
      <td>字段类型 sfixed64。</td>
    </tr>
    <tr>
      <td><code>TYPE_SINT32</code></td>
      <td>字段类型 sint32。</td>
    </tr>
    <tr>
      <td><code>TYPE_SINT64</code></td>
      <td>字段类型 sint64。</td>
    </tr>
  </tbody>
</table>

## FieldMask {#field-mask}

`FieldMask` 表示一组符号化的字段路径，例如：

```proto
paths: "f.a"
paths: "f.b.d"
```

这里 `f` 代表某个根消息中的一个字段，`a` 和 `b` 代表 `f` 中消息里的字段，
而 `d` 代表 `f.b` 中消息里的一个字段。

字段掩码用于指定应由 get 操作（即*投影*）返回、或由更新操作修改的字段子集。
字段掩码还有自定义的 JSON 编码（encoding）（见下文）。

#### 投影中的字段掩码 {#field-masks-projections}

当 `FieldMask` 指定*投影*时，API 会过滤响应消息（或子消息），使其只包含掩码中
指定的字段。例如，考虑这条“掩码前”的响应消息：

```proto
f {
  a : 22
  b {
    d : 1
    x : 2
  }
  y : 13
}
z: 8
```

应用上一示例中的掩码后，API 响应将不包含字段 x、y 或 z 的具体值
（它们的值会被设为默认值，并在 proto 文本输出中省略）：

```proto
f {
  a : 22
  b {
    d : 1
  }
}
```

除字段掩码的最后一段之外，不允许出现 repeated 字段。

如果 get 操作中未提供 `FieldMask` 对象，则该操作适用于所有字段
（就像指定了包含所有字段的 FieldMask 一样）。

请注意，字段掩码不一定应用于顶层响应消息。对于 REST get 操作，字段掩码直接应用于
响应；而对于 REST list 操作，掩码则应用于返回的资源列表中的每一条消息。对于 REST
自定义方法，可以使用其他定义。掩码的应用位置会在 API 中随其声明一同明确记录。
无论如何，掩码对返回资源的影响都是 API 必须实现的行为。

#### 更新操作中的字段掩码 {#field-masks-updates}

更新操作中的字段掩码指定目标资源的哪些字段将被更新。API 必须只更改掩码所指定字段的
值，其余字段保持原样。如果传入一个资源来描述更新后的值，API 会忽略掩码未覆盖的
所有字段的值。

要将字段的值重置为默认值，该字段必须出现在掩码中，并在提供的资源中被设置为默认值。
因此，要重置资源的所有字段，请提供该资源的默认实例并在掩码中设置所有字段，或者
如下文所述不提供掩码。

如果更新时未提供字段掩码，则该操作适用于所有字段（就像指定了包含所有字段的字段掩码
一样）。请注意，在模式演进的情况下，这可能意味着客户端不知道、因而未填入请求的字段
将被重置为其默认值。如果这是不希望的行为，特定服务可以要求客户端始终指定字段掩码，
否则产生错误。

与 get 操作一样，请求消息中描述更新后值的资源位置取决于操作类型。无论如何，
API 都必须遵循字段掩码的效果。

##### HTTP REST 的注意事项 {#http-rest}

使用字段掩码的更新操作，其 HTTP 类型必须设置为 PATCH 而不是 PUT，以满足 HTTP 语义
（PUT 只能用于完整更新）。

#### 字段掩码的 JSON 编码 {#json-encoding-field-masks}

在 JSON 中，字段掩码被编码为单个字符串，其中各路径以逗号分隔。每个路径中的字段名
会按 lowerCamel 命名约定进行相互转换。

例如，考虑以下消息声明：

```proto
message Profile {
  User user = 1;
  Photo photo = 2;
}
message User {
  string display_name = 1;
  string address = 2;
}
```

在 proto 中，`Profile` 的字段掩码可能如下所示：

```proto
mask {
  paths: "user.display_name"
  paths: "photo"
}
```

在 JSON 中，同一掩码表示如下：

```json
{
  mask: "user.displayName,photo"
}
```

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>paths</code></td>
      <td><code>string</code></td>
      <td>字段掩码路径的集合。</td>
    </tr>
  </tbody>
</table>

## FloatValue {#float-value}

`float` 的包装消息。

`FloatValue` 的 JSON 表示形式是 JSON 数字。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code>float</code></td>
      <td>float 值。</td>
    </tr>
  </tbody>
</table>

## Int32Value {#int32-value}

`int32` 的包装消息。

`Int32Value` 的 JSON 表示形式是 JSON 数字。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code>int32</code></td>
      <td>int32 值。</td>
    </tr>
  </tbody>
</table>

## Int64Value {#int64-value}

`int64` 的包装消息。

`Int64Value` 的 JSON 表示形式是 JSON 字符串。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code>int64</code></td>
      <td>int64 值。</td>
    </tr>
  </tbody>
</table>

## ListValue {#list-value}

`ListValue` 是对一个由值组成的 repeated 字段的包装。

`ListValue` 的 JSON 表示形式是 JSON 数组。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>values</code></td>
      <td>
        <code><a href="#value">Value</a></code>
      </td>
      <td>动态类型值的 repeated 字段。</td>
    </tr>
  </tbody>
</table>

## Method {#method}

Method 表示一个 api 的方法。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>name</code></td>
      <td><code>string</code></td>
      <td>此方法的简单名称。</td>
    </tr>
    <tr>
      <td><code>request_type_url</code></td>
      <td><code>string</code></td>
      <td>输入消息类型的 URL。</td>
    </tr>
    <tr>
      <td><code>request_streaming</code></td>
      <td><code>bool</code></td>
      <td>如果为 true，则请求是流式的。</td>
    </tr>
    <tr>
      <td><code>response_type_url</code></td>
      <td><code>string</code></td>
      <td>输出消息类型的 URL。</td>
    </tr>
    <tr>
      <td><code>response_streaming</code></td>
      <td><code>bool</code></td>
      <td>如果为 true，则响应是流式的。</td>
    </tr>
    <tr>
      <td><code>options</code></td>
      <td>
        <code><a href="#option">Option</a></code>
      </td>
      <td>附加到该方法的任意元数据。</td>
    </tr>
    <tr>
      <td><code>syntax</code></td>
      <td>
        <code><a href="#syntax">Syntax</a></code>
      </td>
      <td>此方法的源语法。</td>
    </tr>
  </tbody>
</table>

## Mixin {#mixin}

声明一个要被包含进本 API 的 API。包含方 API 必须重新声明被包含 API 的全部方法，
但文档和选项按如下方式继承：

-   如果在剥离注释和空白之后，重新声明的方法的文档字符串为空，则将从原始方法继承。

-   属于服务配置（http、visibility）且未在重新声明的方法中设置的每项注解都将被继承。

-   如果继承了 http 注解，路径模式将按如下方式修改：任何版本前缀都会被替换为包含方
    API 的版本，再加上 `root` 路径（如果指定）。

简单 mixin 的示例：

```proto
package google.acl.v1;
service AccessControl {
  // 获取底层 ACL 对象。
  rpc GetAcl(GetAclRequest) returns (Acl) {
    option (google.api.http).get = "/v1/{resource=**}:getAcl";
  }
}

package google.storage.v2;
service Storage {
  //       rpc GetAcl(GetAclRequest) returns (Acl);

  // 获取一条数据记录。
  rpc GetData(GetDataRequest) returns (Data) {
    option (google.api.http).get = "/v2/{resource=**}";
  }
}
```

mixin 配置的示例：

```
apis:
- name: google.storage.v2.Storage
  mixins:
  - name: google.acl.v1.AccessControl
```

mixin 结构意味着 `AccessControl` 中的所有方法也会在 `Storage` 中以相同的名称和
请求/响应类型声明。文档生成器或注解处理器在继承文档和注解之后，看到的实际
`Storage.GetAcl` 方法如下：

```proto
service Storage {
  // 获取底层 ACL 对象。
  rpc GetAcl(GetAclRequest) returns (Acl) {
    option (google.api.http).get = "/v2/{resource=**}:getAcl";
  }
  ...
}
```

注意路径模式中的版本如何从 `v1` 变成了 `v2`。

如果指定了 mixin 中的 `root` 字段，它应当是一个相对路径，被继承的 HTTP 路径都会
置于其下。示例：

```
apis:
- name: google.storage.v2.Storage
  mixins:
  - name: google.acl.v1.AccessControl
    root: acls
```

这意味着会有如下被继承的 HTTP 注解：

```proto
service Storage {
  // 获取底层 ACL 对象。
  rpc GetAcl(GetAclRequest) returns (Acl) {
    option (google.api.http).get = "/v2/acls/{resource=**}:getAcl";
  }
  ...
}
```

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>name</code></td>
      <td><code>string</code></td>
      <td>被包含 API 的完全限定名称。</td>
    </tr>
    <tr>
      <td><code>root</code></td>
      <td><code>string</code></td>
      <td>
        如果非空，则指定一个路径，被继承的 HTTP 路径都以该路径为根。
      </td>
    </tr>
  </tbody>
</table>

## NullValue {#null-value}

`NullValue` 是一个单例枚举，用于表示 `Value` 类型联合的空值。

`NullValue` 的 JSON 表示形式是 JSON `null`。

<table>
  <thead>
    <tr>
      <th>枚举值</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>NULL_VALUE</code></td>
      <td>空值。</td>
    </tr>
  </tbody>
</table>

## Option {#option}

一个 Protobuf 选项，可以附加到消息、字段、枚举等之上。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>name</code></td>
      <td><code>string</code></td>
      <td>
        选项的名称。例如 <code>&quot;java_package&quot;</code>。
      </td>
    </tr>
    <tr>
      <td><code>value</code></td>
      <td>
        <code><a href="#any">Any</a></code>
      </td>
      <td>
        选项的值。例如
        <code>&quot;com.google.protobuf&quot;</code>。
      </td>
    </tr>
  </tbody>
</table>

## SourceContext {#source-context}

`SourceContext` 表示有关 Protobuf 元素来源的信息，例如定义它的文件。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>file_name</code></td>
      <td><code>string</code></td>
      <td>
        包含相关 Protobuf 元素的 .proto 文件的带路径限定名称。例如：
        <code>&quot;google/protobuf/source.proto&quot;</code>。
      </td>
    </tr>
  </tbody>
</table>

## StringValue {#string-value}

`string` 的包装消息。

`StringValue` 的 JSON 表示形式是 JSON 字符串。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code>string</code></td>
      <td>string 值。</td>
    </tr>
  </tbody>
</table>

## Struct {#struct}

`Struct` 表示一个结构化数据（structured data）值，由映射到动态类型值的字段组成。
在某些语言中，`Struct` 可能由原生表示形式支持。例如，在 JS 这样的脚本语言中，
struct 表示为对象。该表示形式的细节会随该语言的 proto 支持一并描述。

`Struct` 的 JSON 表示形式是 JSON 对象。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>fields</code></td>
      <td>
        <code>map&lt;string, <a href="#value">Value</a>&gt;</code>
      </td>
      <td>动态类型值的映射。</td>
    </tr>
  </tbody>
</table>

## Syntax {#syntax}

Protobuf 元素定义时所用的语法。

<table>
  <thead>
    <tr>
      <th>枚举值</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>SYNTAX_PROTO2</code></td>
      <td>语法为 <code>proto2</code>。</td>
    </tr>
    <tr>
      <td><code>SYNTAX_PROTO3</code></td>
      <td>语法为 <code>proto3</code>。</td>
    </tr>
    <tr>
      <td><code>SYNTAX_EDITIONS</code></td>
      <td>语法使用 <code>edition</code> 构造。</td>
    </tr>
  </tbody>
</table>

## Timestamp {#timestamp}

Timestamp 表示一个独立于任何时区或日历的时间点，以 UTC 纪元时间的秒数和纳秒分辨率的
秒的小数部分表示。它采用前推格里历（Proleptic Gregorian Calendar）编码，该历法将
格里历向后扩展到公元 1 年。编码时假定每分钟都是 60 秒，即闰秒被“平滑”（smear）
处理，因此解释时无需闰秒表。范围为 0001-01-01T00:00:00Z 到
9999-12-31T23:59:59.999999999Z。通过限制在该范围内，我们确保可以与 RFC 3339 日期
字符串相互转换。参见
<https://www.ietf.org/rfc/rfc3339.txt>。

Timestamp 类型被编码为 RFC 3339 格式的字符串：
“`{year}-{month}-{day}T{hour}:{min}:{sec}[.{frac_sec}]Z`”，其中 `{year}` 始终用
四位数字表示，而 `{month}`、`{day}`、`{hour}`、`{min}` 和 `{sec}` 各自补零到两位。
小数秒最多可有 9 位（即最高 1 纳秒分辨率），为可选。“Z” 后缀表示时区（“UTC”）；
时区是必需的。proto3 JSON 序列化器在输出 Timestamp 类型时应始终使用 UTC
（以 “Z” 表示），而 proto3 JSON 解析器应能同时接受 UTC 和其他时区
（以偏移量表示）。

示例 1：从 POSIX `time()` 计算 Timestamp。

```cpp
Timestamp timestamp;
timestamp.set_seconds(time(NULL));
timestamp.set_nanos(0);
```

示例 2：从 POSIX `gettimeofday()` 计算 Timestamp。

```cpp
struct timeval tv;
gettimeofday(&tv, NULL);

Timestamp timestamp;
timestamp.set_seconds(tv.tv_sec);
timestamp.set_nanos(tv.tv_usec * 1000);
```

示例 3：从 Win32 `GetSystemTimeAsFileTime()` 计算 Timestamp。

```cpp
FILETIME ft;
GetSystemTimeAsFileTime(&ft);
UINT64 ticks = (((UINT64)ft.dwHighDateTime) << 32) | ft.dwLowDateTime;

// 一个 Windows tick 是 100 纳秒。Windows 纪元 1601-01-01T00:00:00Z
// 比 Unix 纪元 1970-01-01T00:00:00Z 早 11644473600 秒。
Timestamp timestamp;
timestamp.set_seconds((INT64) ((ticks / 10000000) - 11644473600LL));
timestamp.set_nanos((INT32) ((ticks % 10000000) * 100));
```

示例 4：从 Java `System.currentTimeMillis()` 计算 Timestamp。

```java
long millis = System.currentTimeMillis();

Timestamp timestamp = Timestamp.newBuilder().setSeconds(millis / 1000)
    .setNanos((int) ((millis % 1000) * 1000000)).build();
```

示例 5：在 Python 中从当前时间计算 Timestamp。

```py
now = time.time()
seconds = int(now)
nanos = int((now - seconds) * 10**9)
timestamp = Timestamp(seconds=seconds, nanos=nanos)
```

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>seconds</code></td>
      <td><code>int64</code></td>
      <td>
        表示自 Unix 纪元 1970-01-01T00:00:00Z 起的 UTC 秒数。
        必须介于 0001-01-01T00:00:00Z 到 9999-12-31T23:59:59Z 之间（含边界）。
      </td>
    </tr>
    <tr>
      <td><code>nanos</code></td>
      <td><code>int32</code></td>
      <td>
        纳秒分辨率下非负的秒的小数部分。带小数部分的负秒值仍必须具有沿时间向前
        计数的非负 nanos 值。必须介于 0 到 999,999,999 之间（含边界）。
      </td>
    </tr>
  </tbody>
</table>

## Type {#type}

一个 Protobuf 消息类型。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>name</code></td>
      <td><code>string</code></td>
      <td>完全限定的消息名称。</td>
    </tr>
    <tr>
      <td><code>fields</code></td>
      <td>
        <code><a href="#field">Field</a></code>
      </td>
      <td>字段列表。</td>
    </tr>
    <tr>
      <td><code>oneofs</code></td>
      <td><code>string</code></td>
      <td>
        此类型的 <code>oneof</code> 定义中出现的类型列表。
      </td>
    </tr>
    <tr>
      <td><code>options</code></td>
      <td>
        <code><a href="#option">Option</a></code>
      </td>
      <td>Protobuf 选项。</td>
    </tr>
    <tr>
      <td><code>source_context</code></td>
      <td>
        <code><a href="#source-context">SourceContext</a></code>
      </td>
      <td>源上下文。</td>
    </tr>
    <tr>
      <td><code>syntax</code></td>
      <td>
        <code><a href="#syntax">Syntax</a></code>
      </td>
      <td>源语法。</td>
    </tr>
  </tbody>
</table>

## UInt32Value {#uint32-value}

`uint32` 的包装消息。

`UInt32Value` 的 JSON 表示形式是 JSON 数字。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code>uint32</code></td>
      <td>uint32 值。</td>
    </tr>
  </tbody>
</table>

## UInt64Value {#uint64-value}

`uint64` 的包装消息。

`UInt64Value` 的 JSON 表示形式是 JSON 字符串。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>value</code></td>
      <td><code>uint64</code></td>
      <td>uint64 值。</td>
    </tr>
  </tbody>
</table>

## Value {#value}

`Value` 表示一个动态类型的值，可以是 null、数字、字符串、布尔值、递归的 struct 值
或值列表。值的产生方应设置其中一种变体；任何变体都缺失则表示错误。

`Value` 的 JSON 表示形式是 JSON 值。

<table>
  <thead>
    <tr>
      <th>字段名</th>
      <th>类型</th>
      <th>说明</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="3">联合字段，以下字段只能设置其中一个：</td>
    </tr>
    <tr>
      <td><code>null_value</code></td>
      <td>
        <code><a href="#null-value">NullValue</a></code>
      </td>
      <td>表示一个空值。</td>
    </tr>
    <tr>
      <td><code>number_value</code></td>
      <td><code>double</code></td>
      <td>
        表示一个 double 值。注意，尝试序列化 NaN 或 Infinity 会导致错误。
        （我们无法像对常规字段那样把它们序列化为字符串 "NaN" 或
        "Infinity"，因为那样它们会被解析为 string_value，而不是 number_value。）
      </td>
    </tr>
    <tr>
      <td><code>string_value</code></td>
      <td><code>string</code></td>
      <td>表示一个字符串值。</td>
    </tr>
    <tr>
      <td><code>bool_value</code></td>
      <td><code>bool</code></td>
      <td>表示一个布尔值。</td>
    </tr>
    <tr>
      <td><code>struct_value</code></td>
      <td>
        <code><a href="#struct">Struct</a></code>
      </td>
      <td>表示一个结构化值。</td>
    </tr>
    <tr>
      <td><code>list_value</code></td>
      <td>
        <code><a href="#list-value">ListValue</a></code>
      </td>
      <td>表示一个 repeated 的 <code>Value</code>。</td>
    </tr>
  </tbody>
</table>
