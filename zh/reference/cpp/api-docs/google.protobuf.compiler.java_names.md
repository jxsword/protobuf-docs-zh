+++
title = "java_names.h"
toc_hide = "true"
linkTitle = "C++"
description = "本节包含在 C++ 中使用 Protobuf 类的参考文档。"
type = "docs"
source_url = "https://protobuf.dev/reference/cpp/api-docs/google.protobuf.compiler.java_names/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-20"
status = "translated"
translator = "agent"
+++

<p><code>#include &lt;google/protobuf/compiler/java/java_names.h&gt;<br>namespace <a href="#google.protobuf.compiler">google::protobuf::compiler::java</a></code></p><p>提供一种把描述符（descriptor）映射到对应 Java 类完全限定（fully-qualified）名称的机制。 </p><table width="100%"><tr><th colspan="2"><h3 style="margin-top: 4px">本文件中的类</h3></th></tr></table><table><tr><th colspan="2"><h3 style="margin-top: 4px">文件成员</h3><div style="font-style: italic; font-weight: normal;">这些定义不属于任何类。</div></th></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="ClassName"><div style="padding-left: 16px; text-indent: -16px"><code><b>ClassName</b>(const <a href='google.protobuf.descriptor#Descriptor'>Descriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#ClassName.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="ClassName"><div style="padding-left: 16px; text-indent: -16px"><code><b>ClassName</b>(const <a href='google.protobuf.descriptor#EnumDescriptor'>EnumDescriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#ClassName.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="ClassName"><div style="padding-left: 16px; text-indent: -16px"><code><b>ClassName</b>(const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#ClassName.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="ClassName"><div style="padding-left: 16px; text-indent: -16px"><code><b>ClassName</b>(const <a href='google.protobuf.descriptor#ServiceDescriptor'>ServiceDescriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#ClassName.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="FileJavaPackage"><div style="padding-left: 16px; text-indent: -16px"><code><b>FileJavaPackage</b>(const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#FileJavaPackage.details">更多…</a></div></td></tr><tr><td style="border-right-width: 0px; text-align: right;"><code>std::string</code></td><td style="border-left-width: 0px"id="CapitalizedFieldName"><div style="padding-left: 16px; text-indent: -16px"><code><b>CapitalizedFieldName</b>(const <a href='google.protobuf.descriptor#FieldDescriptor'>FieldDescriptor</a> * descriptor)</code></div><div style="font-style: italic; margin-top: 4px; margin-left: 16px;">前置条件：  <a href="#CapitalizedFieldName.details">更多…</a></div></td></tr></table> <hr><h3 id="ClassName.details"><code>std::string java::ClassName(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#Descriptor'>Descriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>
<p>返回：</p>

<pre>The fully-qualified Java class name.</pre>
</div> <hr><h3 id="ClassName.details"><code>std::string java::ClassName(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#EnumDescriptor'>EnumDescriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>

<p>返回：</p>

<pre>The fully-qualified Java class name.</pre>
</div> <hr><h3 id="ClassName.details"><code>std::string java::ClassName(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>

<p>返回：</p>

<pre>The fully-qualified Java class name.</pre>
</div> <hr><h3 id="ClassName.details"><code>std::string java::ClassName(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#ServiceDescriptor'>ServiceDescriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>

<p>返回：</p>

<pre>The fully-qualified Java class name.</pre>
</div> <hr><h3 id="FileJavaPackage.details"><code>std::string java::FileJavaPackage(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#FileDescriptor'>FileDescriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>

<p>返回：</p>

<pre>Java package name.</pre>
</div> <hr><h3 id="CapitalizedFieldName.details"><code>std::string java::CapitalizedFieldName(<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;const <a href='google.protobuf.descriptor#FieldDescriptor'>FieldDescriptor</a> * descriptor)</code></h3><div style="margin-left: 16px"><p>前置条件：</p><pre>descriptor != NULL</pre>

<p>返回：</p>

<pre>Capitalized camel case name field name.</pre>

</div>
