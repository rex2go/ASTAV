# ASTAV - Advanced Survey Tools And Validation
ASTAV is tool which is currently under development for validation of CSV results of surveys

## ASD
ASD (Advanced Survey Definition) is the driving definition language of ASTAV.
It supports following instructions:
1. ensure
2. expect
3. print
4. call
5. (soon) limit

"or" and "||" as controlling keyword to enable condition like behavior

There are two variants of writing ASD

Default style:
```
which_pet text ensure(~has_pet, "Ja") expect(["Hund", "Katze"]) or ensure(~has_pet, "Nein") expect(["Keins"])
```
Code style: 
```
which_pet text ensure(~has_pet, "Ja").expect(["Hund", "Katze"]) || ensure(~has_pet, "Nein").expect(["Keins"])
```

It may depend on the length of your instruction set which would make more sense.

## TODOs
### Check possibility of changing order for checks
Currently, entry by entry gets checked - I prefer column by column (maybe make it an option?)
### ~~Implement "call" function~~
~~Calls a passed python function (e.g. for custom mapping purposes)~~
### ~~Fix naming conventions~~
~~It is unclear when things are called commands, functions or instructions~~
### Implement "limit(max, [min])"
### Documentation
As the project grows, documentation is needed
### Add CLI script
### Move commands / functions in own files
### Add optional arguments support
e.g. any?
### Add optional header area 
Header area for optional definitions of custom imported functions and future features