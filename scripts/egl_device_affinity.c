/* Process-local EGL device selection for Blender headless workers on Linux/glibc.
 * CUDA_VISIBLE_DEVICES does not bind OpenGL. Match NVIDIA EGL devices by CUDA PCI ID.
 * Constants and ABI: Khronos EGL_EXT_device_enumeration/query/platform_device.
 */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <limits.h>

typedef void *(*Lookup)(void *, const char *);
typedef void *(*GetProc)(const char *);
typedef unsigned int (*QueryDevices)(int, void **, int *);
typedef const char *(*QueryDeviceString)(void *, int);
typedef unsigned int (*QueryDeviceAttrib)(void *, int, long *);
typedef int (*CudaInit)(unsigned int);
typedef int (*CudaPci)(char *, int, int);
typedef void *(*GetPlatformDisplay)(unsigned int, void *, const int *);
typedef void *(*GetDisplay)(void *);

static Lookup native_lookup(void) {
    return (Lookup)dlvsym(RTLD_NEXT, "dlsym", "GLIBC_2.2.5");
}

static GetProc native_get_proc(void) {
    static GetProc function = NULL;
    if (!function) {
        void *library = dlopen("libEGL.so.1", RTLD_NOW | RTLD_LOCAL);
        function = (GetProc)native_lookup()(library, "eglGetProcAddress");
    }
    return function;
}

void *eglGetDisplay(void *native_display) {
    const char *requested = getenv("ASTRA_EGL_PCI_BUS_ID");
    if (!requested) {
        void *library = dlopen("libEGL.so.1", RTLD_NOW | RTLD_LOCAL);
        return ((GetDisplay)native_lookup()(library, "eglGetDisplay"))(native_display);
    }
    GetProc get_proc = native_get_proc();
    QueryDevices query = (QueryDevices)get_proc("eglQueryDevicesEXT");
    QueryDeviceAttrib attrib = (QueryDeviceAttrib)get_proc("eglQueryDeviceAttribEXT");
    GetPlatformDisplay platform = (GetPlatformDisplay)get_proc("eglGetPlatformDisplayEXT");
    void *devices[64];
    int count = 0;
    void *cuda = dlopen("libcuda.so.1", RTLD_NOW | RTLD_LOCAL);
    CudaInit initialize = cuda ? (CudaInit)native_lookup()(cuda, "cuInit") : NULL;
    CudaPci pci = cuda ? (CudaPci)native_lookup()(cuda, "cuDeviceGetPCIBusId") : NULL;
    char candidate[32];
    if (query && attrib && platform && initialize && pci && initialize(0) == 0 && query(64, devices, &count)) {
        for (int index = 0; index < count; ++index) {
            long ordinal = -1;
            if (attrib(devices[index], 0x323A, &ordinal) && ordinal >= 0 &&
                pci(candidate, sizeof(candidate), (int)ordinal) == 0 && strcasecmp(candidate, requested) == 0) {
                fprintf(stderr, "ASTRA_EGL_DEVICE PCI=%s CUDA_ORDINAL=%ld\n", candidate, ordinal);
                return platform(0x313F, devices[index], NULL); /* EGL_PLATFORM_DEVICE_EXT */
            }
        }
    }
    fprintf(stderr, "ASTRA_EGL_DEVICE_ERROR: requested NVIDIA PCI GPU unavailable; refusing fallback\n");
    _exit(86);
}

void *eglGetProcAddress(const char *name) {
    if (strcmp(name, "eglGetDisplay") == 0) return (void *)eglGetDisplay;
    return native_get_proc()(name);
}

void *dlsym(void *handle, const char *name) {
    if (strcmp(name, "eglGetDisplay") == 0) return (void *)eglGetDisplay;
    if (strcmp(name, "eglGetProcAddress") == 0) return (void *)eglGetProcAddress;
    return native_lookup()(handle, name);
}
