#include <kamek.hpp>
#include <IO/NANDIO.hpp>

namespace Pulsar {

bool NANDIO::CreateAndOpen(const char *path, u32 mode) {
    this->GetCorrectPath(this->filePath, path);
    ISFS::CreateFile(this->filePath, 0, IOS::MODE_READ_WRITE, IOS::MODE_READ_WRITE, IOS::MODE_READ_WRITE);
    return this->OpenFileDirectly(this->filePath, mode);
}

bool NANDIO::OpenFile(const char *path, u32 mode) {
    this->GetCorrectPath(this->filePath, path);
    return this->OpenFileDirectly(this->filePath, mode);
}

void NANDIO::GetCorrectPath(char *realPath, const char *path) const {
    snprintf(realPath, IOS::ipcMaxPath, "%s%s", "/shared2/Pulsar", path);
}

bool NANDIO::FolderExists(const char *path) const {
    char realPath[IOS::ipcMaxPath];
    this->GetCorrectPath(realPath, path);
    u32 count;
    return ISFS::ReadDir(realPath, nullptr, &count) >= 0;
}

bool NANDIO::CreateFolder(const char *path) {
    if (type != IOType_ISO) {
        this->Bind(path);
        char realPath[IOS::ipcMaxPath];
        this->GetCorrectPath(realPath, path);
        s32 error = ISFS::CreateDir(realPath, 0, IOS::MODE_READ_WRITE, IOS::MODE_READ_WRITE, IOS::MODE_READ_WRITE);
        return error >= 0 || error == ISFS::ERROR_FILE_EXISTS;
    }
    return false;
}

void NANDIO::ReadFolder(const char *path) {
    if (this->isBusy) return;
    this->isBusy = true;
    this->fileCount = 0;
    if (this->fileNames != nullptr) delete[] this->fileNames;
    this->fileNames = nullptr;
    this->Bind(path);
    char realPath[IOS::ipcMaxPath];
    this->GetCorrectPath(realPath, path);

    u32 count = maxFileCount;
    const u32 capacity = 255 * (maxFileCount + 1);
    char *buffer = new (this->heap, 0x20) char[capacity];
    if (buffer == nullptr) {
        this->isBusy = false;
        return;
    }
    memset(buffer, 0, capacity);
    const s32 error = ISFS::ReadDir(realPath, buffer, &count);
    if (error >= 0 && count > 0 && count <= maxFileCount) {
        IOS::IPCPath *namesArray = new (this->heap, 0x20) IOS::IPCPath[count];
        if (namesArray != nullptr) {
            u32 realCount = 0;
            u32 offset = 0;
            char curFile[IOS::ipcMaxPath];
            // ReadDir returns count NUL-terminated names, not a double-NUL list.
            // Bound both the entry count and every string scan to the allocation.
            for (u32 entry = 0; entry < count && offset < capacity; ++entry) {
                const char *name = buffer + offset;
                u32 length = 0;
                while (length < capacity - offset && name[length] != '\0') ++length;
                if (length == 0 || length == capacity - offset || length > 255) break;
                if (length <= IOS::ipcMaxFileName) {
                    const int written = snprintf(curFile, IOS::ipcMaxPath, "%s/%s", realPath, name);
                    if (written >= 0 && static_cast<u32>(written) < IOS::ipcMaxPath) {
                        const s32 curFilefd = ISFS::Open(curFile, ISFS::MODE_NONE);
                        if (curFilefd >= 0) {
                            snprintf(namesArray[realCount], IOS::ipcMaxPath, "%s", name);
                            ++realCount;
                            ISFS::Close(curFilefd);
                        }
                    }
                }
                offset += length + 1;
            }
            this->fileCount = realCount;
            this->fileNames = namesArray;
        }
    }
    EGG::Heap::free(buffer, this->heap);
    this->isBusy = false;
}

bool NANDIO::RenameFile(const char *oldPath, const char *newPath) const {
    char realOldPath[IOS::ipcMaxPath];
    char realNewPath[IOS::ipcMaxPath];
    this->GetCorrectPath(realOldPath, oldPath);
    this->GetCorrectPath(realNewPath, newPath);
    return ISFS::Rename(realOldPath, realNewPath) >= 0;
}

}  // namespace Pulsar
