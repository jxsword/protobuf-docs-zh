

+++
title = "type_resolver_util.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.util.type_resolver_util/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-21"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/util/type_resolver_util.h&gt;<br>namespace <a href="#google.protobuf.util">google::protobuf::util</a></code></p><p>为 TypeResolver 定义实用工具。 </p><table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr></table><table><tr><th colspan="2"><h3 style="margin-top: 4px">文件级成员</h3><div style="font-style: italic; font-weight: normal;">这些定义不属于任何类。</div></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code><a href='google.protobuf.util.type_resolver#TypeResolver'>TypeResolver</a> *</code></td><td style="border-left-width: 0px"id="NewTypeResolverForDescriptorPool"><div style="padding-left: 16px; text-indent: -16px"><code><b>NewTypeResolverForDescriptorPool</b>(const std::string &amp; url_prefix, const <a href='google.protobuf.descriptor#DescriptorPool'>DescriptorPool</a> * pool)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">创建一个在给定描述符池（descriptor pool）中提供类型信息的 TypeResolver。  <a href="#NewTypeResolverForDescriptorPool.details">更多…</a></div></td></tr></table> <hr><h3 id="NewTypeResolverForDescriptorPool.details"><code><a href='google.protobuf.util.type_resolver#TypeResolver'>TypeResolver</a> * util::NewTypeResolverForDescriptorPool(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const std::string &amp; url_prefix,<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#DescriptorPool'>DescriptorPool</a> * pool)</code></h3><div style="margin-left: 16px"><p>创建一个在给定描述符池中提供类型信息的 TypeResolver。 </p><p>调用者拥有所返回 <a href='google.protobuf.util.type_resolver#TypeResolver'>TypeResolver</a> 的所有权。 </p>

</div>
