+++
source_url = "https://protobuf.dev/reference/kotlin/api-docs/protobuf-kotlin/com.google.protobuf.kotlin/-dsl-proxy/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-21"
status = "translated"
translator = "agent"
+++

//[protobuf-kotlin](/reference/kotlin/api-docs/)/[com.google.protobuf.kotlin](/reference/kotlin/api-docs/protobuf-kotlin/com.google.protobuf.kotlin/)/DslProxy

# DslProxy

[JVM] abstract class [DslProxy]()

一种仅因其存在而有意义的类型，从不打算被实例化。例如，可以为 DslList<Int, FooProxy> 赋予与 DslList<Int, BarProxy> 不同的扩展方法（extension methods）。
