---
title: STL getline读入\r问题
author: Jinkai
date: 2021-02-25 09:00:00 +0800
published: true
categories: [技术]
tags: [stl, c++, getline]
---

## getline说明

-------

std::getline (string)

- istream& getline (istream& is, string& str, char delim);
- istream& getline (istream& is, string& str);

### Get line from stream into string

Extracts characters from is and stores them into str until the delimitation character delim is found (or the newline character, '\n', for (2)).

>读取到'`\n`'作为结束

The extraction also stops if the end of file is reached in is or if some other error occurs during the input operation.

If the delimiter is found, it is extracted and discarded (i.e. it is not stored and the next input operation will begin after it).

Note that any content in str before the call is replaced by the newly extracted sequence.

Each extracted character is appended to the string as if its member push_back was called.

### Parameters

- is - istream object from which characters are extracted.

- str - string object where the extracted line is stored.
The contents in the string before the call (if any) are discarded and replaced by the extracted line.

### Return Value

The same as parameter is.

A call to this function may set any of the internal state flags of is if:

| flag | error |
| :---: | :---|
|eofbit|The end of the source of characters is reached during its operations.|
|failbit|The input obtained could not be interpreted as a valid textual representation of an object of this type. In this case, distr preserves the parameters and internal data it had before the call.Notice that some eofbit cases will also set failbit.|
|badbit|An error other than the above happened.|

(see ios_base::iostate for more info on these)

Additionally, in any of these cases, if the appropriate flag has been set with is's member function ios::exceptions, an exception of type ios_base::failure is thrown.

## 出现的错误

-------

使用vscode编辑txt格式文件时，默认的换行符为`CRLF`，即`\r\n`，而getline的默认分隔符为`\n`，导致`\r`也被读入string，造成乱码

## 参考

- [getline (string) - C++ Reference](<http://www.cplusplus.com/reference/string/string/getline/>)
