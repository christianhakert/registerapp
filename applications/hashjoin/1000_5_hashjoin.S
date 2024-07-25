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
mov            x19                 ,192                 
movk           x19                 ,0                   ,lsl 16              
movk           x19                 ,0                   ,lsl 32              
movk           x19                 ,0                   ,lsl 48              
sub            sp                  ,sp                  ,x19                 
//__start of relation
mov            x19                 ,4224                
movk           x19                 ,51857               ,lsl 16              
movk           x19                 ,43690               ,lsl 32              
movk           x19                 ,0                   ,lsl 48              
adr x19, relation_1      
//__end of relation
loop_head0:
mov            x20                 ,28224               
movk           x20                 ,51857               ,lsl 16              
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
mov            x18                 ,16                  
str            x18                 ,[sp,0]              
ldr            x18                 ,[sp,0]              
ldr            x23                 ,[x19,x18]           
// --- selection
mov            x18                 ,500                 
str            x18                 ,[sp,8]              
movk           x18                 ,0                   ,lsl 16              
str            x18                 ,[sp,8]              
movk           x18                 ,0                   ,lsl 32              
str            x18                 ,[sp,8]              
movk           x18                 ,0                   ,lsl 48              
str            x18                 ,[sp,8]              
ldr            x18                 ,[sp,8]              
cmp            x22                 ,x18                 
b.ge           nextTuple0          
// --- hash join build
//__hashtable_base
mov            x18                 ,2688                
str            x18                 ,[sp,16]             
movk           x18                 ,51859               ,lsl 16              
str            x18                 ,[sp,16]             
movk           x18                 ,43690               ,lsl 32              
str            x18                 ,[sp,16]             
movk           x18                 ,0                   ,lsl 48              
adr x18, sht
str            x18                 ,[sp,16]             
// func call {
mov            x1                  ,x22                 
ldr            x0                  ,[sp,16]             
sub            sp                  ,sp                  ,16                  
// mov            x30                 ,48144               
// movk           x30                 ,45844               ,lsl 16              
// movk           x30                 ,43690               ,lsl 32              
// movk           x30                 ,0                   ,lsl 48              
// blr            x30                 
bl ht_put
add            sp                  ,sp                  ,16                  
str            x0                  ,[sp,24]             
// } end call
// --- materialize HT entry
mov            x18                 ,0                   
str            x18                 ,[sp,32]             
ldr            x18                 ,[sp,24]             
ldr            x17                 ,[sp,32]             
str            x21                 ,[x18,x17]           
mov            x18                 ,8                   
str            x18                 ,[sp,40]             
ldr            x18                 ,[sp,24]             
ldr            x17                 ,[sp,40]             
str            x22                 ,[x18,x17]           
mov            x18                 ,16                  
str            x18                 ,[sp,48]             
ldr            x18                 ,[sp,24]             
ldr            x17                 ,[sp,48]             
str            x23                 ,[x18,x17]           
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
mov            x19                 ,36480               
movk           x19                 ,51860               ,lsl 16              
movk           x19                 ,43690               ,lsl 32              
movk           x19                 ,0                   ,lsl 48              
adr x19, outrel  
//__start of relation
mov            x20                 ,29440               
movk           x20                 ,51857               ,lsl 16              
movk           x20                 ,43690               ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
adr x20, relation_2
//__end of relation
loop_head1:
mov            x21                 ,45440               
movk           x21                 ,51857               ,lsl 16              
movk           x21                 ,43690               ,lsl 32              
movk           x21                 ,0                   ,lsl 48              
adr x21, outrel
cmp            x20                 ,x21                 
b.ge           loop_foot1          
// --- dematerialize
mov            x23                 ,0                   
ldr            x22                 ,[x20,x23]           
mov            x18                 ,8                   
str            x18                 ,[sp,56]             
ldr            x18                 ,[sp,56]             
ldr            x23                 ,[x20,x18]           
// --- selection
mov            x18                 ,500                 
str            x18                 ,[sp,64]             
movk           x18                 ,0                   ,lsl 16              
str            x18                 ,[sp,64]             
movk           x18                 ,0                   ,lsl 32              
str            x18                 ,[sp,64]             
movk           x18                 ,0                   ,lsl 48              
str            x18                 ,[sp,64]             
ldr            x18                 ,[sp,64]             
cmp            x22                 ,x18                 
b.ge           nextTuple1          
// --- hash join probe
mov            x18                 ,0                   
str            x18                 ,[sp,80]             
movk           x18                 ,0                   ,lsl 16              
str            x18                 ,[sp,80]             
movk           x18                 ,0                   ,lsl 32              
str            x18                 ,[sp,80]             
movk           x18                 ,0                   ,lsl 48              
str            x18                 ,[sp,80]             
loop_head2:
mov            x18                 ,2688                
str            x18                 ,[sp,72]             
movk           x18                 ,51859               ,lsl 16              
str            x18                 ,[sp,72]             
movk           x18                 ,43690               ,lsl 32              
str            x18                 ,[sp,72]             
movk           x18                 ,0                   ,lsl 48              
str            x18                 ,[sp,72]             
// func call {
mov            x1                  ,x22                 
ldr            x0                  ,[sp,72]             
ldr            x2                  ,[sp,80]             
sub            sp                  ,sp                  ,16                  
//mov            x30                 ,47072               
//movk           x30                 ,45844               ,lsl 16              
//movk           x30                 ,43690               ,lsl 32              
//movk           x30                 ,0                   ,lsl 48              
//blr            x30                 
bl            ht_get                 
add            sp                  ,sp                  ,16                  
str            x0                  ,[sp,80]             
// } end call
ldr            x18                 ,[sp,80]             
cmp            x18                 ,0                   
b.eq           loop_foot2          
// --- dematerialize HT entry
mov            x18                 ,0                   
str            x18                 ,[sp,96]             
ldr            x17                 ,[sp,80]             
ldr            x16                 ,[sp,96]             
ldr            x18                 ,[x17,x16]           
str            x18                 ,[sp,88]             
mov            x18                 ,8                   
str            x18                 ,[sp,112]            
ldr            x17                 ,[sp,80]             
ldr            x16                 ,[sp,112]            
ldr            x18                 ,[x17,x16]           
str            x18                 ,[sp,104]            
mov            x18                 ,16                  
str            x18                 ,[sp,128]            
ldr            x17                 ,[sp,80]             
ldr            x16                 ,[sp,128]            
ldr            x18                 ,[x17,x16]           
str            x18                 ,[sp,120]            
// --- materialize
mov            x18                 ,40                  
str            x18                 ,[sp,136]            
movk           x18                 ,0                   ,lsl 16              
str            x18                 ,[sp,136]            
movk           x18                 ,0                   ,lsl 32              
str            x18                 ,[sp,136]            
movk           x18                 ,0                   ,lsl 48              
str            x18                 ,[sp,136]            
mov            x18                 ,0                   
str            x18                 ,[sp,144]            
ldr            x18                 ,[sp,88]             
ldr            x17                 ,[sp,144]            
str            x18                 ,[x19,x17]           
mov            x18                 ,8                   
str            x18                 ,[sp,152]            
ldr            x18                 ,[sp,104]            
ldr            x17                 ,[sp,152]            
str            x18                 ,[x19,x17]           
mov            x18                 ,16                  
str            x18                 ,[sp,160]            
ldr            x18                 ,[sp,120]            
ldr            x17                 ,[sp,160]            
str            x18                 ,[x19,x17]           
mov            x18                 ,24                  
str            x18                 ,[sp,168]            
ldr            x18                 ,[sp,168]            
str            x22                 ,[x19,x18]           
mov            x18                 ,32                  
str            x18                 ,[sp,176]            
ldr            x18                 ,[sp,176]            
str            x23                 ,[x19,x18]           
ldr            x18                 ,[sp,136]            
add            x19                 ,x19                 ,x18                 
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
mov            x20                 ,36480               
movk           x20                 ,51860               ,lsl 16              
movk           x20                 ,43690               ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
sub            x19                 ,x19                 ,x20                 
mov            x20                 ,40                  
movk           x20                 ,0                   ,lsl 16              
movk           x20                 ,0                   ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
udiv           x19                 ,x19                 ,x20                 
mov            x20                 ,520                 
movk           x20                 ,62392               ,lsl 16              
movk           x20                 ,65535               ,lsl 32              
movk           x20                 ,0                   ,lsl 48              
str            x19                 ,[x20]               
mov            x19                 ,192                 
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