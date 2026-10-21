.DEFAULT_GOAL := all
PYTHON ?= python3
MKNITRO_SINGLE_CONFIG ?= 0
CC := mwcceppc.exe
AS := mwasmeppc.exe

COMMIT_HASH := $(shell git rev-parse --short HEAD 2>/dev/null || echo source-archive)
GAMESOURCE := ./GameSource
PULSAR := ./PulsarEngine
SECURE := ./external/rr-secure
SECURE_EXISTS := $(shell test -d "$(SECURE)" && echo 1)
SECURE_INCLUDE := $(if $(SECURE_EXISTS),-i $(SECURE),)
SECURE_EXTERNALS := $(if $(SECURE_EXISTS),-externals=$(SECURE)/anticheat.txt,)
KAMEK := Kamek.exe
KAMEK_H := ./KamekInclude
KAMEK_LOADER := ./Loader

ifneq ($(filter install%,$(MAKECMDGOALS)),)
PULSAR_RANDOM_KEY := $(shell $(PYTHON) -c "import random; print(hex(random.randint(0, 0xFFFFFFFF)))")
$(info [PULSAR] Random Room Key generated: $(PULSAR_RANDOM_KEY))
else
PULSAR_RANDOM_KEY := 0xADD2BFAF
endif

# See https://stackoverflow.com/questions/51727566/
VERSION_FILE := PulsarEngine/Version.cpp

-include .env

PROFILE_FLAGS := $(if $(filter 1,$(MKNITRO_SINGLE_CONFIG)),-DMKNITRO_SINGLE_CONFIG,)
# Match the recovered October C++ compiler flags; assembly retains its Gekko target.
override CFLAGS := -I- -i $(KAMEK_H) -i $(GAMESOURCE) $(SECURE_INCLUDE) -i $(PULSAR) -i $(KAMEK_LOADER) \
		  -opt all -inline auto -enum int -fp hard -sdata 0 -sdata2 0 -maxerrors 1 \
		  -func_align 4 -DMKNITRO_SERVER -DPULSAR_RANDOM_KEY=$(PULSAR_RANDOM_KEY) $(PROFILE_FLAGS) $(CFLAGS)
ASFLAGS := -proc gekko -c

EXTERNALS := -externals=$(GAMESOURCE)/symbols.txt -externals=$(GAMESOURCE)/anticheat.txt $(SECURE_EXTERNALS) -versions=$(GAMESOURCE)/versions.txt

# Source files
CPP_SRCS := $(sort $(shell find $(PULSAR) -type f -name "*.cpp") $(PULSAR)/Version.cpp)
ASM_SRCS := $(shell find $(PULSAR) -type f -name "*.S")
SECURE_CPP_SRCS := $(if $(SECURE_EXISTS),$(shell find $(SECURE) -type f -name "*.cpp"),)
SECURE_ASM_SRCS := $(if $(SECURE_EXISTS),$(shell find $(SECURE) -type f -name "*.S"),)
PULSAR_CPP_SRCS := $(filter-out $(foreach src,$(SECURE_CPP_SRCS),$(PULSAR)/$(patsubst $(SECURE)/%,%,$(src))),$(CPP_SRCS))
PULSAR_ASM_SRCS := $(filter-out $(foreach src,$(SECURE_ASM_SRCS),$(PULSAR)/$(patsubst $(SECURE)/%,%,$(src))),$(ASM_SRCS))

# Object files
CPP_OBJS := $(patsubst $(PULSAR)/%.cpp, build/PulsarEngine/%.o, $(PULSAR_CPP_SRCS))
ASM_OBJS := $(patsubst $(PULSAR)/%.S, build/PulsarEngine/%.o, $(PULSAR_ASM_SRCS))
SECURE_CPP_OBJS := $(patsubst $(SECURE)/%.cpp, build/secure/%.o, $(SECURE_CPP_SRCS))
SECURE_ASM_OBJS := $(patsubst $(SECURE)/%.S, build/secure/%.o, $(SECURE_ASM_SRCS))

OBJS := $(CPP_OBJS) $(ASM_OBJS) $(SECURE_CPP_OBJS) $(SECURE_ASM_OBJS)

all: build force_link

.PHONY: all force_link clean test preflight check-integration FORCE_VERSION

preflight:
	@$(PYTHON) scripts/check_toolchain.py --cc "$(CC)" --assembler "$(AS)" --linker "$(KAMEK)"

check-integration:
	$(PYTHON) scripts/test_integration.py

FORCE_VERSION:

$(VERSION_FILE): FORCE_VERSION | preflight
	@$(PYTHON) scripts/write_version.py

# Some inherited header names contain spaces; use a content stamp instead of
# expanding their paths as a whitespace-delimited make prerequisite list.
.PHONY: FORCE_HEADERS
FORCE_HEADERS:
build/header-stamp: FORCE_HEADERS | build
	@$(PYTHON) scripts/generate_drift_colours.py
	@$(PYTHON) scripts/write_header_stamp.py
$(OBJS) build/kamek.o: build/header-stamp | preflight

test:
	@echo "CPP sources:"
	@echo "$(CPP_SRCS)"
	@echo "ASM sources:"
	@echo "$(ASM_SRCS)"

build:
	@mkdir -p build/PulsarEngine

build/kamek.o: $(KAMEK_H)/kamek.cpp build/header-stamp | build
	@$(CC) $(CFLAGS) -c -o $@ $<

# C++ compilation
build/PulsarEngine/%.o: $(PULSAR)/%.cpp build/header-stamp | build
	@echo Compiling C++ $(PULSAR)/$*.cpp...
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -c -o $@ $(PULSAR)/$*.cpp

# Assembly compilation (.S)
build/PulsarEngine/%.o: $(PULSAR)/%.S | build
	@echo Assembling $<...
	@mkdir -p $(dir $@)
	@$(AS) $(ASFLAGS) -o $@ $<

# External security sources
build/secure/%.o: $(SECURE)/%.cpp | build
	@echo Compiling Secure C++ $<...
	@mkdir -p $(dir $@)
	@$(CC) $(CFLAGS) -c -o $@ $<

build/secure/%.o: $(SECURE)/%.S | build
	@echo Assembling Secure $<...
	@mkdir -p $(dir $@)
	@$(AS) $(ASFLAGS) -o $@ $<

build/Network/RoomKey.o: .force

.force:

force_link: build/kamek.o $(OBJS)
	@echo Linking...
	@$(KAMEK) $^ -dynamic $(EXTERNALS) '-output-kamek=build/Code.$$KV$$.bin' -output-map=build/Code.map
	$(PYTHON) scripts/combine_bin.py -p build/Code.P.bin \
		-e build/Code.E.bin -j build/Code.J.bin -o build/Code.pul
	$(PYTHON) scripts/apply_release_policy.py build/Code.pul --report build/release-policy.json

install:
	@echo "Use scripts/stage_candidate.py --output NEW_FOLDER for an isolated test pack."
	@echo "The uploaded CurrentPack snapshot is never overwritten by make."

clean:
	@echo Cleaning...
	@rm -rf build


LOADER_CPP_SRCS := $(KAMEK_LOADER)/mkw.cpp $(KAMEK_LOADER)/kamekLoader.cpp
LOADER_OBJS := $(patsubst $(KAMEK_LOADER)/%.cpp, build/Loader/%.o, $(LOADER_CPP_SRCS))
$(LOADER_OBJS): build/header-stamp | preflight

.PHONY: build_loader loader

loader: build_loader link_loader

build_loader:
	@mkdir -p build/Loader

build/Loader/%.o: $(KAMEK_LOADER)/%.cpp build/header-stamp | build_loader
	@echo Compiling C++ $(KAMEK_LOADER)/$*.cpp...
	@$(CC) $(CFLAGS) -c -o $@ $(KAMEK_LOADER)/$*.cpp

link_loader: $(LOADER_OBJS)
	@$(KAMEK) $^ -static=0x80004000 -output-code=build/Loader.pul -output-map=build/Loader.map
