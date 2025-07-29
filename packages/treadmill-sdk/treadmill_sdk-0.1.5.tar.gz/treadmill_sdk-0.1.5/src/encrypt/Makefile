# 设置变量
SCRIPT_DIR := $(shell pwd)
LIB_DIR := $(abspath $(SCRIPT_DIR)/dist/shared/mac)  # 仍保留自定义路径，但会被 pkg-config 覆盖

# 使用 pkg-config 获取 OpenSSL 配置
CFLAGS := $(shell pkg-config --cflags openssl) -Wall -O2 -g
LDFLAGS := $(shell pkg-config --libs-only-L openssl)
LIBS := $(shell pkg-config --libs-only-l openssl)

# 设置编译器
CC := gcc
CXX := g++

# 编译选项
CFLAGS += -g -Wall
CXXFLAGS := -g -Wall -std=c++17

# 获取所有 .c 和 .cpp 文件
C_SOURCES := $(wildcard *.c)
CPP_SOURCES := $(wildcard *.cpp)
BINARIES := $(C_SOURCES:.c=) $(CPP_SOURCES:.cpp=)

# 编译 C 文件
%: %.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@.exe $< $(LIBS)
	@echo "\033[1;33m[mac] build $@.c done\033[0m"

# 编译 C++ 文件
%: %.cpp
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@.exe $< $(LIBS)
	@echo "\033[1;33m[mac] build $@.cpp done\033[0m"

# 默认目标
all: $(BINARIES)

# 清理目标
clean:
	rm -f $(addsuffix .exe,$(BINARIES))
	rm -rf $(addsuffix .exe.dSYM,$(BINARIES))

# 运行目标
run:
	 ./aes_gcm_openssl.exe

.PHONY: all clean run
