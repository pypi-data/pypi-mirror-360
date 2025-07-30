#/* record_stubs.c - stub implementations to satisfy record symbols */
#include "config.h"
#include <sys/types.h>
#include <netinet/in.h>
#include "record.h"

int record_init(char *file) { return 0; }
int record(u_int32_t src, u_int32_t dst, int proto,
           u_short sport, u_short dport,
           char *name, u_char *buf, int len) { return 0; }
void record_dump(void) { }
void record_close(void) { }