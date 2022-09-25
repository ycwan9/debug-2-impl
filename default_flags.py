CFALGS = [
    "-Werror=conditional-uninitialized",
    "-Werror=format-insufficient-args",
    "-Werror=format-pedantic",
    "-Werror=implicit-function-declaration",
    "-Werror=implicit-int",
    "-Werror=incompatible-library-redeclaration",
    "-Werror=incompatible-pointer-types",
    "-Werror=int-conversion",
    "-Werror=pedantic",
    "-Werror=return-type",
    "-Werror=sometimes-uninitialized",
    "-Werror=uninitialized",
    "-Werror=uninitialized-const-reference",
    "-Wno-error=extra-semi",
    "-Wno-error=gnu-line-marker",
    "-Wno-error=gnu-statement-expression",
    "-Wno-error=gnu-statement-expression-from-macro-expansion",
    "-DUSE_MATH_MACROS",
    "-g"
]
CFALGS_UNOPT = ["-O0"]
CFALGS_OPT = ["-Og"]
CLANG = "clang"

