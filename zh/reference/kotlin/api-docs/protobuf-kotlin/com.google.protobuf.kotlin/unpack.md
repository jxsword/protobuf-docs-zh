+++
source_url = "https://protobuf.dev/reference/kotlin/api-docs/protobuf-kotlin/com.google.protobuf.kotlin/unpack/"
upstream_commit = "f72a6a648b34e9e098cbce1519bc9c8139105d66"
translated_at = "2026-11-21"
status = "translated"
translator = "agent"
+++

//[protobuf-kotlin](/reference/kotlin/api-docs/)/[com.google.protobuf.kotlin](/reference/kotlin/api-docs/protobuf-kotlin/com.google.protobuf.kotlin/)/unpack

# unpack

[JVM] \
Content \
inline fun <[T]() :
[Message](/reference/java/api-docs/com/google/protobuf/Message.html)>
[Any](/reference/java/api-docs/com/google/protobuf/Any.html).[unpack]()():
[T]() 

返回此
[com.google.protobuf.Any](/reference/java/api-docs/com/google/protobuf/Any.html)
中编码的 T 类型消息（message）。

#### 异常

                                                                                                                                |     |
------------------------------------------------------------------------------------------------------------------------------- | ---
<a name="com.google.protobuf.kotlin//unpack/com.google.protobuf.Any#/PointingToDeclaration/"></a>InvalidProtocolBufferException | <a name="com.google.protobuf.kotlin//unpack/com.google.protobuf.Any#/PointingToDeclaration/"></a><br><br>如果此 [com.google.protobuf.Any](/reference/java/api-docs/com/google/protobuf/Any.html) 中不包含 T 消息。<br><br>
