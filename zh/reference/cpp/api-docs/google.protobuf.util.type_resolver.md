

+++
title = "type_resolver.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.util.type_resolver/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-21"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/util/type_resolver.h&gt;<br>namespace <a href="#google.protobuf.util">google::protobuf::util</a></code></p><p>为 Any 消息（message）定义一个 TypeResolver。 </p><table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr><tr><td><div><code><a href="#TypeResolver">TypeResolver</a></code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">类型解析器（type resolver）的抽象接口。 </div></td></tr></table><h2 id="TypeResolver">class TypeResolver</h2><p><code>#include &lt;<a href="#">google/protobuf/util/type_resolver.h</a>&gt;<br>namespace <a href="#google.protobuf.util">google::protobuf::util</a></code></p><p>类型解析器的抽象接口。 </p><p>此接口的实现必须是线程安全的。 </p>

<table><tr><th colspan="2"><h3 style="margin-top: 4px">成员</h3></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code></code></td><td style="border-left-width: 0px"id="TypeResolver.TypeResolver"><div style="padding-left: 16px; text-indent: -16px"><code><b>TypeResolver</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual </code></td><td style="border-left-width: 0px"id="TypeResolver.~TypeResolver"><div style="padding-left: 16px; text-indent: -16px"><code><b>~TypeResolver</b>()</code></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual util::Status</code></td><td style="border-left-width: 0px"id="TypeResolver.ResolveMessageType"><div style="padding-left: 16px; text-indent: -16px"><code><b>ResolveMessageType</b>(const std::string &amp; type_url, google::protobuf::Type * message_type)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">为消息类型解析 type url。 </div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>virtual util::Status</code></td><td style="border-left-width: 0px"id="TypeResolver.ResolveEnumType"><div style="padding-left: 16px; text-indent: -16px"><code><b>ResolveEnumType</b>(const std::string &amp; type_url, google::protobuf::Enum * enum_type)  = 0</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">为枚举类型解析 type url。 </div></td></tr></table>
