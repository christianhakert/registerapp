.section .text
.globl hashjoin
hashjoin:
// --- scan
stp            x19                 ,x20                 ,[sp,-16]!           
stp            x21                 ,x22                 ,[sp,-16]!           
stp            x23                 ,x24                 ,[sp,-16]!           
stp            x25                 ,x26                 ,[sp,-16]!           
stp            x27                 ,x28                 ,[sp,-16]!           
stp            x29                 ,x30                 ,[sp,-16]!           
mov            x19                 ,16                  
movk           x19                 ,0                   ,lsl 16              
movk           x19                 ,0                   ,lsl 32              
movk           x19                 ,0                   ,lsl 48              
sub            sp                  ,sp                  ,x19                 
//__start of relation
mov            x19                 ,32896               
movk           x19                 ,53403               ,lsl 16              
movk           x19                 ,43690               ,lsl 32              
movk           x19                 ,0                   ,lsl 48              
adr x19, relation_1
//__end of relation
loop_head0:
mov            x20                 ,56896               
movk           x20                 ,53403               ,lsl 16              
movk           x20                 ,43690               ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
adr x20, relation_2
cmp            x19                 ,x20                 
b.ge           loop_foot0          
// --- dematerialize
mov            x22                 ,0                   
ldr            x21                 ,[x19,x22]           
mov            x23                 ,8                   
ldr            x22                 ,[x19,x23]           
mov            x24                 ,16                  
ldr            x23                 ,[x19,x24]           
// --- selection
mov            x24                 ,500                 
movk           x24                 ,0                   ,lsl 16              
movk           x24                 ,0                   ,lsl 32              
movk           x24                 ,0                   ,lsl 48              
cmp            x22                 ,x24                 
b.ge           nextTuple0          
// --- hash join build
//__hashtable_base
mov            x24                 ,31360               
movk           x24                 ,53405               ,lsl 16              
movk           x24                 ,43690               ,lsl 32              
movk           x24                 ,0                   ,lsl 48              
adr x24, sht
// func call {
mov            x0                  ,x24                 
mov            x1                  ,x22                 
sub            sp                  ,sp                  ,16                  
//mov            x30                 ,48144               
//movk           x30                 ,50429               ,lsl 16              
//movk           x30                 ,43690               ,lsl 32              
//movk           x30                 ,0                   ,lsl 48              
//blr            x30                 
bl ht_put
add            sp                  ,sp                  ,16                  
mov            x25                 ,x0                  
// } end call
// --- materialize HT entry
mov            x24                 ,0                   
str            x21                 ,[x25,x24]           
mov            x24                 ,8                   
str            x22                 ,[x25,x24]           
mov            x24                 ,16                  
str            x23                 ,[x25,x24]           
// --- scan tail
nextTuple0:
mov            x21                 ,24                  
movk           x21                 ,0                   ,lsl 16              
movk           x21                 ,0                   ,lsl 32              
movk           x21                 ,0                   ,lsl 48              
add            x19                 ,x19                 ,x21                 
b              loop_head0          
loop_foot0:
// --- scan
mov            x19                 ,65152               
movk           x19                 ,53406               ,lsl 16              
movk           x19                 ,43690               ,lsl 32              
movk           x19                 ,0                   ,lsl 48              
adr x19, outrel
//__start of relation
mov            x20                 ,58112               
movk           x20                 ,53403               ,lsl 16              
movk           x20                 ,43690               ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
adr x20, relation_2
//__end of relation
loop_head1:
mov            x21                 ,8576                
movk           x21                 ,53404               ,lsl 16              
movk           x21                 ,43690               ,lsl 32              
movk           x21                 ,0                   ,lsl 48              
adr x21, outrel
cmp            x20                 ,x21                 
b.ge           loop_foot1          
// --- dematerialize
mov            x23                 ,0                   
ldr            x22                 ,[x20,x23]           
mov            x24                 ,8                   
ldr            x23                 ,[x20,x24]           
// --- selection
mov            x24                 ,500                 
movk           x24                 ,0                   ,lsl 16              
movk           x24                 ,0                   ,lsl 32              
movk           x24                 ,0                   ,lsl 48              
cmp            x22                 ,x24                 
b.ge           nextTuple1          
// --- hash join probe
mov            x25                 ,0                   
movk           x25                 ,0                   ,lsl 16              
movk           x25                 ,0                   ,lsl 32              
movk           x25                 ,0                   ,lsl 48              
loop_head2:
mov            x24                 ,31360               
movk           x24                 ,53405               ,lsl 16              
movk           x24                 ,43690               ,lsl 32              
movk           x24                 ,0                   ,lsl 48              
// func call {
mov            x0                  ,x24                 
mov            x1                  ,x22                 
mov            x2                  ,x25                 
sub            sp                  ,sp                  ,16                  
//mov            x30                 ,47072               
//movk           x30                 ,50429               ,lsl 16              
//movk           x30                 ,43690               ,lsl 32              
//movk           x30                 ,0                   ,lsl 48              
//blr            x30                 
bl            ht_get
add            sp                  ,sp                  ,16                  
mov            x25                 ,x0                  
// } end call
cmp            x25                 ,0                   
b.eq           loop_foot2          
// --- dematerialize HT entry
mov            x26                 ,0                   
ldr            x24                 ,[x25,x26]           
mov            x27                 ,8                   
ldr            x26                 ,[x25,x27]           
mov            x28                 ,16                  
ldr            x27                 ,[x25,x28]           
// --- materialize
mov            x28                 ,40                  
movk           x28                 ,0                   ,lsl 16              
movk           x28                 ,0                   ,lsl 32              
movk           x28                 ,0                   ,lsl 48              
mov            x29                 ,0                   
str            x24                 ,[x19,x29]           
mov            x29                 ,8                   
str            x26                 ,[x19,x29]           
mov            x29                 ,16                  
str            x27                 ,[x19,x29]           
mov            x29                 ,24                  
str            x22                 ,[x19,x29]           
mov            x29                 ,32                  
str            x23                 ,[x19,x29]           
add            x19                 ,x19                 ,x28                 
b              loop_head2          
loop_foot2:
// --- scan tail
nextTuple1:
mov            x22                 ,16                  
movk           x22                 ,0                   ,lsl 16              
movk           x22                 ,0                   ,lsl 32              
movk           x22                 ,0                   ,lsl 48              
add            x20                 ,x20                 ,x22                 
b              loop_head1          
loop_foot1:
mov            x20                 ,65152               
movk           x20                 ,53406               ,lsl 16              
movk           x20                 ,43690               ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
sub            x19                 ,x19                 ,x20                 
mov            x20                 ,40                  
movk           x20                 ,0                   ,lsl 16              
movk           x20                 ,0                   ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
udiv           x19                 ,x19                 ,x20                 
mov            x20                 ,39928               
movk           x20                 ,62254               ,lsl 16              
movk           x20                 ,65535               ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
str            x19                 ,[x20]               
mov            x19                 ,16                  
movk           x19                 ,0                   ,lsl 16              
movk           x19                 ,0                   ,lsl 32              
movk           x19                 ,0                   ,lsl 48              
add            sp                  ,sp                  ,x19                 
ldp            x29                 ,x30                 ,[sp], 16            
ldp            x27                 ,x28                 ,[sp], 16            
ldp            x25                 ,x26                 ,[sp], 16            
ldp            x23                 ,x24                 ,[sp], 16            
ldp            x21                 ,x22                 ,[sp], 16            
ldp            x19                 ,x20                 ,[sp], 16            
ret