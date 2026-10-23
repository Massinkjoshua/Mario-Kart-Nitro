
#include <cassert>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <new>
#include <string>
#include <vector>
using u32=unsigned; using s32=int;
struct FakeHeap {};
static int allocations, failAllocation, openCalls, closeCalls, dirCalls;
static int resultCode; static unsigned returnedCount; static bool rejectOpen;
static std::string listing;
void* operator new[](std::size_t n, FakeHeap*, int) noexcept {
    if (++allocations == failAllocation) return nullptr;
    void* p=::operator new[](n); memset(p,0xa5,n); return p;
}
namespace EGG { struct Heap { static void free(void* p,FakeHeap*) { ::operator delete[](p); } }; }
namespace IOS { const unsigned ipcMaxPath=64, ipcMaxFileName=12; typedef char IPCPath[64]; }
namespace ISFS {
const int MODE_NONE=0;
int ReadDir(const char*,char* out,unsigned* count) {
 ++dirCalls; assert(*count==100); assert(listing.size()<=255*101);
 memcpy(out,listing.data(),listing.size());*count=returnedCount;return resultCode;
}
int Open(const char*,int) {++openCalls;return rejectOpen ? -1 : 10;}
int Close(int) {++closeCalls;return 0;}
}
namespace Pulsar {
const int maxFileCount=100;
class NANDIO {public:
 FakeHeap* heap=nullptr; bool isBusy=false; unsigned fileCount=0; IOS::IPCPath* fileNames=nullptr;
 char folderName[64]={};
 ~NANDIO(){delete[] fileNames;}
 void Bind(const char* p){snprintf(folderName,64,"%s",p);}
 void GetCorrectPath(char* out,const char* p) const {snprintf(out,64,"/shared2/Pulsar%s",p);}
 void ReadFolder(const char*);
};
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

}
void reset(unsigned count,std::string bytes,int error=0,int fail=0){
 allocations=openCalls=closeCalls=dirCalls=0;failAllocation=fail;returnedCount=count;listing=bytes;resultCode=error;rejectOpen=false;
}
int main(){
 int checks=0;
 {Pulsar::NANDIO io;reset(0,"");io.ReadFolder("/test");assert(io.fileCount==0&&io.fileNames==nullptr&&!io.isBusy&&openCalls==0);++checks;}
 {Pulsar::NANDIO io;reset(1,std::string("one.rkg\0phantom.rkg\0",20));io.ReadFolder("/test");assert(io.fileCount==1&&openCalls==1&&closeCalls==1&&std::string(io.fileNames[0])=="one.rkg");++checks;}
 {Pulsar::NANDIO io;std::string bytes;for(int i=0;i<100;++i){bytes+="a.rkg";bytes+='\0';}reset(100,bytes);io.ReadFolder("/test");assert(io.fileCount==100&&openCalls==100&&!io.isBusy);++checks;}
 {Pulsar::NANDIO io;reset(101,"a");io.ReadFolder("/test");assert(io.fileCount==0&&openCalls==0&&!io.isBusy);++checks;}
 {Pulsar::NANDIO io;reset(1,std::string(255*101,'x'));io.ReadFolder("/test");assert(io.fileCount==0&&openCalls==0&&!io.isBusy);++checks;}
 for(int fail=1;fail<=2;++fail){Pulsar::NANDIO io;reset(1,std::string("a\0",2),0,fail);io.ReadFolder("/test");assert(io.fileCount==0&&io.fileNames==nullptr&&!io.isBusy&&openCalls==0);++checks;}
 {Pulsar::NANDIO io;reset(1,std::string("a\0",2),-1);io.ReadFolder("/test");assert(io.fileCount==0&&openCalls==0&&!io.isBusy);++checks;}
 {Pulsar::NANDIO io;reset(1,std::string("a\0",2));rejectOpen=true;io.ReadFolder("/test");assert(io.fileCount==0&&openCalls==1&&closeCalls==0&&!io.isBusy);++checks;}
 {Pulsar::NANDIO io;reset(1,std::string("a\0",2));io.ReadFolder("/test");assert(io.fileCount==1);reset(0,"");io.ReadFolder("/test");assert(io.fileCount==0&&io.fileNames==nullptr&&!io.isBusy);++checks;}
 {Pulsar::NANDIO io;io.isBusy=true;reset(0,"");io.ReadFolder("/test");assert(dirCalls==0&&io.isBusy);++checks;}
 {Pulsar::NANDIO io;reset(1,std::string("a\0",2));io.ReadFolder("/abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz");assert(openCalls==0&&io.fileCount==0);++checks;}
 printf("%d ghost-folder cases passed\n",checks);
}
