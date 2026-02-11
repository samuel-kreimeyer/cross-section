/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison implementation for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* C LALR(1) parser skeleton written by Richard Stallman, by
   simplifying the original so-called "semantic" parser.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

/* All symbols defined below should begin with yy or YY, to avoid
   infringing on user name space.  This should be done even for local
   variables, as they might otherwise be expanded by user macros.
   There are some unavoidable exceptions within include files to
   define necessary library symbols; they are noted "INFRINGES ON
   USER NAME SPACE" below.  */

/* Identify Bison output, and Bison version.  */
#define YYBISON 30802

/* Bison version string.  */
#define YYBISON_VERSION "3.8.2"

/* Skeleton name.  */
#define YYSKELETON_NAME "yacc.c"

/* Pure parsers.  */
#define YYPURE 0

/* Push parsers.  */
#define YYPUSH 0

/* Pull parsers.  */
#define YYPULL 1

/* Substitute the type names.  */
#define YYSTYPE         GMLSTYPE
/* Substitute the variable and function names.  */
#define yyparse         gmlparse
#define yylex           gmllex
#define yyerror         gmlerror
#define yydebug         gmldebug
#define yynerrs         gmlnerrs
#define yylval          gmllval
#define yychar          gmlchar

/* First part of user prologue.  */
#line 19 "../../cmd/tools/gmlparse.y"

#include <stdlib.h>
#include <string.h>
#include <arith.h>
#include <gml2gv.h>
#include <assert.h>
#include <util/agxbuf.h>
#include <util/alloc.h>
#include <util/exit.h>
#include <util/list.h>

static gmlgraph* G;
static gmlnode* N;
static gmledge* E;

static attrs_t *L;

static void free_attrs(attrs_t *a) {
  LIST_FREE(a);
  free(a);
}

static LIST(attrs_t *) liststk = {.dtor = free_attrs};

static char *sortToStr(unsigned short sort);

static void free_node(gmlnode *p) {
    if (!p) return;
    LIST_FREE(&p->attrlist);
    free(p->id);
    free (p);
}

static void free_edge(gmledge *p) {
    if (!p) return;
    LIST_FREE(&p->attrlist);
    free (p);
}

static void free_graph(gmlgraph *p) {
    if (!p) return;
    LIST_FREE(&p->nodelist);
    LIST_FREE(&p->edgelist);
    LIST_FREE(&p->attrlist);
    LIST_FREE(&p->graphlist);
    free (p);
}

static void
cleanup (void)
{
    LIST_CLEAR(&liststk);
    if (L) {
	free_attrs(L);
	L = NULL;
    }
    if (N) {
	free_node(N);
	N = NULL;
    }
    if (E) {
	free_edge(E);
	E = NULL;
    }
    if (G) {
	free_graph(G);
	G = NULL;
    }
}

static void free_attr(gmlattr *p);

static void
pushAlist (void)
{
    attrs_t *const lp = gv_alloc(sizeof(attrs_t));
    lp->dtor = free_attr;

    if (L) {
	LIST_PUSH_BACK(&liststk, L);
    }
    L = lp;
}

static attrs_t *popAlist(void) {
    attrs_t *lp = L;

    if (!LIST_IS_EMPTY(&liststk))
	L = LIST_POP_BACK(&liststk);
    else
	L = NULL;

    return lp;
}

static void
popG (void)
{
    G = G->parent;
}

static void
pushG (void)
{
    gmlgraph* g = gv_alloc(sizeof(gmlgraph));

    g->attrlist.dtor = free_attr;
    g->nodelist.dtor = free_node;
    g->edgelist.dtor = free_edge;
    g->graphlist.dtor = free_graph;
    g->parent = G;
    g->directed = -1;

    if (G)
	LIST_APPEND(&G->graphlist, g);

    G = g;
}

static gmlnode*
mkNode (void)
{
    gmlnode *const n = gv_alloc(sizeof(gmlnode));
    n->attrlist.dtor = free_attr;
    return n;
}

static gmledge*
mkEdge (void)
{
    gmledge* ep = gv_alloc(sizeof(gmledge));
    ep->attrlist.dtor = free_attr;
    return ep;
}

static gmlattr *mkAttr(char* name, unsigned short sort, unsigned short kind,
                       char* str,  attrs_t* list) {
    gmlattr* gp = gv_alloc(sizeof(gmlattr));

    assert (name || sort);
    if (!name)
	name = gv_strdup (sortToStr (sort));
    gp->sort = sort;
    gp->kind = kind;
    gp->name = name;
    if (str)
	gp->u.value = str;
    else {
	if (list != NULL && LIST_IS_EMPTY(list)) {
	    free_attrs(list);
	    list = 0;
	}
	gp->u.lp = list;
    }
    return gp;
}

static int
setDir (char* d)
{
    gmlgraph* g;
    int dir = atoi (d);

    free (d);
    if (dir < 0) dir = -1;
    else if (dir > 0) dir = 1;
    else dir = 0;
    G->directed = dir;

    if (dir >= 0) {
	for (g = G->parent; g; g = g->parent) {
	    if (g->directed < 0)
		g->directed = dir;
	    else if (g->directed != dir)
		return 1;
        }
    }

    return 0;
}


#line 262 "gmlparse.c"

# ifndef YY_CAST
#  ifdef __cplusplus
#   define YY_CAST(Type, Val) static_cast<Type> (Val)
#   define YY_REINTERPRET_CAST(Type, Val) reinterpret_cast<Type> (Val)
#  else
#   define YY_CAST(Type, Val) ((Type) (Val))
#   define YY_REINTERPRET_CAST(Type, Val) ((Type) (Val))
#  endif
# endif
# ifndef YY_NULLPTR
#  if defined __cplusplus
#   if 201103L <= __cplusplus
#    define YY_NULLPTR nullptr
#   else
#    define YY_NULLPTR 0
#   endif
#  else
#   define YY_NULLPTR ((void*)0)
#  endif
# endif

#include "gmlparse.h"
/* Symbol kind.  */
enum yysymbol_kind_t
{
  YYSYMBOL_YYEMPTY = -2,
  YYSYMBOL_YYEOF = 0,                      /* "end of file"  */
  YYSYMBOL_YYerror = 1,                    /* error  */
  YYSYMBOL_YYUNDEF = 2,                    /* "invalid token"  */
  YYSYMBOL_GRAPH = 3,                      /* GRAPH  */
  YYSYMBOL_NODE = 4,                       /* NODE  */
  YYSYMBOL_EDGE = 5,                       /* EDGE  */
  YYSYMBOL_DIRECTED = 6,                   /* DIRECTED  */
  YYSYMBOL_SOURCE = 7,                     /* SOURCE  */
  YYSYMBOL_TARGET = 8,                     /* TARGET  */
  YYSYMBOL_XVAL = 9,                       /* XVAL  */
  YYSYMBOL_YVAL = 10,                      /* YVAL  */
  YYSYMBOL_WVAL = 11,                      /* WVAL  */
  YYSYMBOL_HVAL = 12,                      /* HVAL  */
  YYSYMBOL_LABEL = 13,                     /* LABEL  */
  YYSYMBOL_GRAPHICS = 14,                  /* GRAPHICS  */
  YYSYMBOL_LABELGRAPHICS = 15,             /* LABELGRAPHICS  */
  YYSYMBOL_TYPE = 16,                      /* TYPE  */
  YYSYMBOL_FILL = 17,                      /* FILL  */
  YYSYMBOL_OUTLINE = 18,                   /* OUTLINE  */
  YYSYMBOL_OUTLINESTYLE = 19,              /* OUTLINESTYLE  */
  YYSYMBOL_OUTLINEWIDTH = 20,              /* OUTLINEWIDTH  */
  YYSYMBOL_WIDTH = 21,                     /* WIDTH  */
  YYSYMBOL_STYLE = 22,                     /* STYLE  */
  YYSYMBOL_LINE = 23,                      /* LINE  */
  YYSYMBOL_POINT = 24,                     /* POINT  */
  YYSYMBOL_TEXT = 25,                      /* TEXT  */
  YYSYMBOL_FONTSIZE = 26,                  /* FONTSIZE  */
  YYSYMBOL_FONTNAME = 27,                  /* FONTNAME  */
  YYSYMBOL_COLOR = 28,                     /* COLOR  */
  YYSYMBOL_INTEGER = 29,                   /* INTEGER  */
  YYSYMBOL_REAL = 30,                      /* REAL  */
  YYSYMBOL_STRING = 31,                    /* STRING  */
  YYSYMBOL_ID = 32,                        /* ID  */
  YYSYMBOL_NAME = 33,                      /* NAME  */
  YYSYMBOL_GML_LIST = 34,                  /* GML_LIST  */
  YYSYMBOL_35_ = 35,                       /* '['  */
  YYSYMBOL_36_ = 36,                       /* ']'  */
  YYSYMBOL_YYACCEPT = 37,                  /* $accept  */
  YYSYMBOL_graph = 38,                     /* graph  */
  YYSYMBOL_hdr = 39,                       /* hdr  */
  YYSYMBOL_body = 40,                      /* body  */
  YYSYMBOL_optglist = 41,                  /* optglist  */
  YYSYMBOL_glist = 42,                     /* glist  */
  YYSYMBOL_glistitem = 43,                 /* glistitem  */
  YYSYMBOL_node = 44,                      /* node  */
  YYSYMBOL_45_1 = 45,                      /* $@1  */
  YYSYMBOL_nlist = 46,                     /* nlist  */
  YYSYMBOL_nlistitem = 47,                 /* nlistitem  */
  YYSYMBOL_edge = 48,                      /* edge  */
  YYSYMBOL_49_2 = 49,                      /* $@2  */
  YYSYMBOL_elist = 50,                     /* elist  */
  YYSYMBOL_elistitem = 51,                 /* elistitem  */
  YYSYMBOL_attrlist = 52,                  /* attrlist  */
  YYSYMBOL_53_3 = 53,                      /* $@3  */
  YYSYMBOL_optalist = 54,                  /* optalist  */
  YYSYMBOL_alist = 55,                     /* alist  */
  YYSYMBOL_alistitem = 56                  /* alistitem  */
};
typedef enum yysymbol_kind_t yysymbol_kind_t;




#ifdef short
# undef short
#endif

/* On compilers that do not define __PTRDIFF_MAX__ etc., make sure
   <limits.h> and (if available) <stdint.h> are included
   so that the code can choose integer types of a good width.  */

#ifndef __PTRDIFF_MAX__
# include <limits.h> /* INFRINGES ON USER NAME SPACE */
# if defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stdint.h> /* INFRINGES ON USER NAME SPACE */
#  define YY_STDINT_H
# endif
#endif

/* Narrow types that promote to a signed type and that can represent a
   signed or unsigned integer of at least N bits.  In tables they can
   save space and decrease cache pressure.  Promoting to a signed type
   helps avoid bugs in integer arithmetic.  */

#ifdef __INT_LEAST8_MAX__
typedef __INT_LEAST8_TYPE__ yytype_int8;
#elif defined YY_STDINT_H
typedef int_least8_t yytype_int8;
#else
typedef signed char yytype_int8;
#endif

#ifdef __INT_LEAST16_MAX__
typedef __INT_LEAST16_TYPE__ yytype_int16;
#elif defined YY_STDINT_H
typedef int_least16_t yytype_int16;
#else
typedef short yytype_int16;
#endif

/* Work around bug in HP-UX 11.23, which defines these macros
   incorrectly for preprocessor constants.  This workaround can likely
   be removed in 2023, as HPE has promised support for HP-UX 11.23
   (aka HP-UX 11i v2) only through the end of 2022; see Table 2 of
   <https://h20195.www2.hpe.com/V2/getpdf.aspx/4AA4-7673ENW.pdf>.  */
#ifdef __hpux
# undef UINT_LEAST8_MAX
# undef UINT_LEAST16_MAX
# define UINT_LEAST8_MAX 255
# define UINT_LEAST16_MAX 65535
#endif

#if defined __UINT_LEAST8_MAX__ && __UINT_LEAST8_MAX__ <= __INT_MAX__
typedef __UINT_LEAST8_TYPE__ yytype_uint8;
#elif (!defined __UINT_LEAST8_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST8_MAX <= INT_MAX)
typedef uint_least8_t yytype_uint8;
#elif !defined __UINT_LEAST8_MAX__ && UCHAR_MAX <= INT_MAX
typedef unsigned char yytype_uint8;
#else
typedef short yytype_uint8;
#endif

#if defined __UINT_LEAST16_MAX__ && __UINT_LEAST16_MAX__ <= __INT_MAX__
typedef __UINT_LEAST16_TYPE__ yytype_uint16;
#elif (!defined __UINT_LEAST16_MAX__ && defined YY_STDINT_H \
       && UINT_LEAST16_MAX <= INT_MAX)
typedef uint_least16_t yytype_uint16;
#elif !defined __UINT_LEAST16_MAX__ && USHRT_MAX <= INT_MAX
typedef unsigned short yytype_uint16;
#else
typedef int yytype_uint16;
#endif

#ifndef YYPTRDIFF_T
# if defined __PTRDIFF_TYPE__ && defined __PTRDIFF_MAX__
#  define YYPTRDIFF_T __PTRDIFF_TYPE__
#  define YYPTRDIFF_MAXIMUM __PTRDIFF_MAX__
# elif defined PTRDIFF_MAX
#  ifndef ptrdiff_t
#   include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  endif
#  define YYPTRDIFF_T ptrdiff_t
#  define YYPTRDIFF_MAXIMUM PTRDIFF_MAX
# else
#  define YYPTRDIFF_T long
#  define YYPTRDIFF_MAXIMUM LONG_MAX
# endif
#endif

#ifndef YYSIZE_T
# ifdef __SIZE_TYPE__
#  define YYSIZE_T __SIZE_TYPE__
# elif defined size_t
#  define YYSIZE_T size_t
# elif defined __STDC_VERSION__ && 199901 <= __STDC_VERSION__
#  include <stddef.h> /* INFRINGES ON USER NAME SPACE */
#  define YYSIZE_T size_t
# else
#  define YYSIZE_T unsigned
# endif
#endif

#define YYSIZE_MAXIMUM                                  \
  YY_CAST (YYPTRDIFF_T,                                 \
           (YYPTRDIFF_MAXIMUM < YY_CAST (YYSIZE_T, -1)  \
            ? YYPTRDIFF_MAXIMUM                         \
            : YY_CAST (YYSIZE_T, -1)))

#define YYSIZEOF(X) YY_CAST (YYPTRDIFF_T, sizeof (X))


/* Stored state numbers (used for stacks). */
typedef yytype_int8 yy_state_t;

/* State numbers in computations.  */
typedef int yy_state_fast_t;

#ifndef YY_
# if defined YYENABLE_NLS && YYENABLE_NLS
#  if ENABLE_NLS
#   include <libintl.h> /* INFRINGES ON USER NAME SPACE */
#   define YY_(Msgid) dgettext ("bison-runtime", Msgid)
#  endif
# endif
# ifndef YY_
#  define YY_(Msgid) Msgid
# endif
#endif


#ifndef YY_ATTRIBUTE_PURE
# if defined __GNUC__ && 2 < __GNUC__ + (96 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_PURE __attribute__ ((__pure__))
# else
#  define YY_ATTRIBUTE_PURE
# endif
#endif

#ifndef YY_ATTRIBUTE_UNUSED
# if defined __GNUC__ && 2 < __GNUC__ + (7 <= __GNUC_MINOR__)
#  define YY_ATTRIBUTE_UNUSED __attribute__ ((__unused__))
# else
#  define YY_ATTRIBUTE_UNUSED
# endif
#endif

/* Suppress unused-variable warnings by "using" E.  */
#if ! defined lint || defined __GNUC__
# define YY_USE(E) ((void) (E))
#else
# define YY_USE(E) /* empty */
#endif

/* Suppress an incorrect diagnostic about yylval being uninitialized.  */
#if defined __GNUC__ && ! defined __ICC && 406 <= __GNUC__ * 100 + __GNUC_MINOR__
# if __GNUC__ * 100 + __GNUC_MINOR__ < 407
#  define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                           \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")
# else
#  define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN                           \
    _Pragma ("GCC diagnostic push")                                     \
    _Pragma ("GCC diagnostic ignored \"-Wuninitialized\"")              \
    _Pragma ("GCC diagnostic ignored \"-Wmaybe-uninitialized\"")
# endif
# define YY_IGNORE_MAYBE_UNINITIALIZED_END      \
    _Pragma ("GCC diagnostic pop")
#else
# define YY_INITIAL_VALUE(Value) Value
#endif
#ifndef YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
# define YY_IGNORE_MAYBE_UNINITIALIZED_END
#endif
#ifndef YY_INITIAL_VALUE
# define YY_INITIAL_VALUE(Value) /* Nothing. */
#endif

#if defined __cplusplus && defined __GNUC__ && ! defined __ICC && 6 <= __GNUC__
# define YY_IGNORE_USELESS_CAST_BEGIN                          \
    _Pragma ("GCC diagnostic push")                            \
    _Pragma ("GCC diagnostic ignored \"-Wuseless-cast\"")
# define YY_IGNORE_USELESS_CAST_END            \
    _Pragma ("GCC diagnostic pop")
#endif
#ifndef YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_BEGIN
# define YY_IGNORE_USELESS_CAST_END
#endif


#define YY_ASSERT(E) ((void) (0 && (E)))

#if !defined yyoverflow

/* The parser invokes alloca or malloc; define the necessary symbols.  */

# ifdef YYSTACK_USE_ALLOCA
#  if YYSTACK_USE_ALLOCA
#   ifdef __GNUC__
#    define YYSTACK_ALLOC __builtin_alloca
#   elif defined __BUILTIN_VA_ARG_INCR
#    include <alloca.h> /* INFRINGES ON USER NAME SPACE */
#   elif defined _AIX
#    define YYSTACK_ALLOC __alloca
#   elif defined _MSC_VER
#    include <malloc.h> /* INFRINGES ON USER NAME SPACE */
#    define alloca _alloca
#   else
#    define YYSTACK_ALLOC alloca
#    if ! defined _ALLOCA_H && ! defined EXIT_SUCCESS
#     include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
      /* Use EXIT_SUCCESS as a witness for stdlib.h.  */
#     ifndef EXIT_SUCCESS
#      define EXIT_SUCCESS 0
#     endif
#    endif
#   endif
#  endif
# endif

# ifdef YYSTACK_ALLOC
   /* Pacify GCC's 'empty if-body' warning.  */
#  define YYSTACK_FREE(Ptr) do { /* empty */; } while (0)
#  ifndef YYSTACK_ALLOC_MAXIMUM
    /* The OS might guarantee only one guard page at the bottom of the stack,
       and a page size can be as small as 4096 bytes.  So we cannot safely
       invoke alloca (N) if N exceeds 4096.  Use a slightly smaller number
       to allow for a few compiler-allocated temporary stack slots.  */
#   define YYSTACK_ALLOC_MAXIMUM 4032 /* reasonable circa 2006 */
#  endif
# else
#  define YYSTACK_ALLOC YYMALLOC
#  define YYSTACK_FREE YYFREE
#  ifndef YYSTACK_ALLOC_MAXIMUM
#   define YYSTACK_ALLOC_MAXIMUM YYSIZE_MAXIMUM
#  endif
#  if (defined __cplusplus && ! defined EXIT_SUCCESS \
       && ! ((defined YYMALLOC || defined malloc) \
             && (defined YYFREE || defined free)))
#   include <stdlib.h> /* INFRINGES ON USER NAME SPACE */
#   ifndef EXIT_SUCCESS
#    define EXIT_SUCCESS 0
#   endif
#  endif
#  ifndef YYMALLOC
#   define YYMALLOC malloc
#   if ! defined malloc && ! defined EXIT_SUCCESS
void *malloc (YYSIZE_T); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
#  ifndef YYFREE
#   define YYFREE free
#   if ! defined free && ! defined EXIT_SUCCESS
void free (void *); /* INFRINGES ON USER NAME SPACE */
#   endif
#  endif
# endif
#endif /* !defined yyoverflow */

#if (! defined yyoverflow \
     && (! defined __cplusplus \
         || (defined GMLSTYPE_IS_TRIVIAL && GMLSTYPE_IS_TRIVIAL)))

/* A type that is properly aligned for any stack member.  */
union yyalloc
{
  yy_state_t yyss_alloc;
  YYSTYPE yyvs_alloc;
};

/* The size of the maximum gap between one aligned stack and the next.  */
# define YYSTACK_GAP_MAXIMUM (YYSIZEOF (union yyalloc) - 1)

/* The size of an array large to enough to hold all stacks, each with
   N elements.  */
# define YYSTACK_BYTES(N) \
     ((N) * (YYSIZEOF (yy_state_t) + YYSIZEOF (YYSTYPE)) \
      + YYSTACK_GAP_MAXIMUM)

# define YYCOPY_NEEDED 1

/* Relocate STACK from its old location to the new one.  The
   local variables YYSIZE and YYSTACKSIZE give the old and new number of
   elements in the stack, and YYPTR gives the new location of the
   stack.  Advance YYPTR to a properly aligned location for the next
   stack.  */
# define YYSTACK_RELOCATE(Stack_alloc, Stack)                           \
    do                                                                  \
      {                                                                 \
        YYPTRDIFF_T yynewbytes;                                         \
        YYCOPY (&yyptr->Stack_alloc, Stack, yysize);                    \
        Stack = &yyptr->Stack_alloc;                                    \
        yynewbytes = yystacksize * YYSIZEOF (*Stack) + YYSTACK_GAP_MAXIMUM; \
        yyptr += yynewbytes / YYSIZEOF (*yyptr);                        \
      }                                                                 \
    while (0)

#endif

#if defined YYCOPY_NEEDED && YYCOPY_NEEDED
/* Copy COUNT objects from SRC to DST.  The source and destination do
   not overlap.  */
# ifndef YYCOPY
#  if defined __GNUC__ && 1 < __GNUC__
#   define YYCOPY(Dst, Src, Count) \
      __builtin_memcpy (Dst, Src, YY_CAST (YYSIZE_T, (Count)) * sizeof (*(Src)))
#  else
#   define YYCOPY(Dst, Src, Count)              \
      do                                        \
        {                                       \
          YYPTRDIFF_T yyi;                      \
          for (yyi = 0; yyi < (Count); yyi++)   \
            (Dst)[yyi] = (Src)[yyi];            \
        }                                       \
      while (0)
#  endif
# endif
#endif /* !YYCOPY_NEEDED */

/* YYFINAL -- State number of the termination state.  */
#define YYFINAL  55
/* YYLAST -- Last index in YYTABLE.  */
#define YYLAST   226

/* YYNTOKENS -- Number of terminals.  */
#define YYNTOKENS  37
/* YYNNTS -- Number of nonterminals.  */
#define YYNNTS  20
/* YYNRULES -- Number of rules.  */
#define YYNRULES  63
/* YYNSTATES -- Number of states.  */
#define YYNSTATES  102

/* YYMAXUTOK -- Last valid token kind.  */
#define YYMAXUTOK   289


/* YYTRANSLATE(TOKEN-NUM) -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex, with out-of-bounds checking.  */
#define YYTRANSLATE(YYX)                                \
  (0 <= (YYX) && (YYX) <= YYMAXUTOK                     \
   ? YY_CAST (yysymbol_kind_t, yytranslate[YYX])        \
   : YYSYMBOL_YYUNDEF)

/* YYTRANSLATE[TOKEN-NUM] -- Symbol number corresponding to TOKEN-NUM
   as returned by yylex.  */
static const yytype_int8 yytranslate[] =
{
       0,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,    35,     2,    36,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     1,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    22,    23,    24,
      25,    26,    27,    28,    29,    30,    31,    32,    33,    34
};

#if GMLDEBUG
/* YYRLINE[YYN] -- Source line where rule number YYN was defined.  */
static const yytype_int16 yyrline[] =
{
       0,   224,   224,   225,   226,   229,   232,   235,   236,   239,
     240,   243,   244,   245,   246,   253,   254,   257,   257,   260,
     261,   264,   265,   268,   268,   271,   272,   275,   276,   277,
     278,   281,   281,   284,   285,   288,   289,   292,   293,   294,
     295,   296,   297,   298,   299,   300,   301,   302,   303,   304,
     305,   306,   307,   308,   309,   310,   311,   312,   313,   314,
     315,   316,   317,   318
};
#endif

/** Accessing symbol of state STATE.  */
#define YY_ACCESSING_SYMBOL(State) YY_CAST (yysymbol_kind_t, yystos[State])

#if GMLDEBUG || 0
/* The user-facing name of the symbol whose (internal) number is
   YYSYMBOL.  No bounds checking.  */
static const char *yysymbol_name (yysymbol_kind_t yysymbol) YY_ATTRIBUTE_UNUSED;

/* YYTNAME[SYMBOL-NUM] -- String name of the symbol SYMBOL-NUM.
   First, the terminals, then, starting at YYNTOKENS, nonterminals.  */
static const char *const yytname[] =
{
  "\"end of file\"", "error", "\"invalid token\"", "GRAPH", "NODE",
  "EDGE", "DIRECTED", "SOURCE", "TARGET", "XVAL", "YVAL", "WVAL", "HVAL",
  "LABEL", "GRAPHICS", "LABELGRAPHICS", "TYPE", "FILL", "OUTLINE",
  "OUTLINESTYLE", "OUTLINEWIDTH", "WIDTH", "STYLE", "LINE", "POINT",
  "TEXT", "FONTSIZE", "FONTNAME", "COLOR", "INTEGER", "REAL", "STRING",
  "ID", "NAME", "GML_LIST", "'['", "']'", "$accept", "graph", "hdr",
  "body", "optglist", "glist", "glistitem", "node", "$@1", "nlist",
  "nlistitem", "edge", "$@2", "elist", "elistitem", "attrlist", "$@3",
  "optalist", "alist", "alistitem", YY_NULLPTR
};

static const char *
yysymbol_name (yysymbol_kind_t yysymbol)
{
  return yytname[yysymbol];
}
#endif

#define YYPACT_NINF (-29)

#define yypact_value_is_default(Yyn) \
  ((Yyn) == YYPACT_NINF)

#define YYTABLE_NINF (-35)

#define yytable_value_is_error(Yyn) \
  0

/* YYPACT[STATE-NUM] -- Index in YYTABLE of the portion describing
   STATE-NUM.  */
static const yytype_int16 yypact[] =
{
       1,   -29,   -24,     0,     2,     3,     5,    11,    11,     6,
      17,    18,    19,    22,   -21,   -28,    11,    11,    21,    24,
      25,    28,    12,    54,    52,   193,   -29,   -29,   -29,   -29,
     -29,   -29,   -29,   -29,   -29,   -29,   -29,   -29,   -29,   -29,
     -29,   -29,   -29,   -29,   -29,   -29,   -29,   -29,   -29,   -29,
     -29,   -29,   -29,   -29,   -29,   -29,   -29,    30,   -29,   193,
      58,   -29,    51,   -29,   -29,    59,    60,    30,    78,    58,
     -29,   -29,   -29,   -29,   -29,    80,    81,   -29,   -29,   -29,
     -29,   -29,   168,   143,    90,   113,   -29,   -29,    91,   114,
     115,    85,   -29,   -29,   -29,   -29,   -29,   -29,   -29,   -29,
     -29,   -29
};

/* YYDEFACT[STATE-NUM] -- Default reduction number in state STATE-NUM.
   Performed when YYTABLE does not specify something else to do.  Zero
   means the default is an error.  */
static const yytype_int8 yydefact[] =
{
       0,     3,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
       0,     0,     0,     0,     0,    33,    36,    42,    41,    43,
      44,    45,    46,    31,    47,    48,    49,    50,    51,    52,
      53,    55,    54,    56,    57,    58,    59,    60,    62,    61,
      63,    37,    38,    39,    40,     1,     5,     0,    35,    34,
       8,     2,     0,    17,    23,     0,     0,     0,     0,     7,
      10,    11,    12,    16,    32,     0,     0,    14,    15,    13,
       6,     9,     0,     0,     0,     0,    20,    22,     0,     0,
       0,     0,    26,    30,    21,    18,    19,    27,    28,    29,
      24,    25
};

/* YYPGOTO[NTERM-NUM].  */
static const yytype_int16 yypgoto[] =
{
     -29,   -29,   118,   105,   -29,   -29,    79,   -29,   -29,   -29,
      62,   -29,   -29,   -29,    82,    23,   -29,   138,   -29,   -25
};

/* YYDEFGOTO[NTERM-NUM].  */
static const yytype_int8 yydefgoto[] =
{
       0,    23,    67,    61,    68,    69,    70,    71,    75,    85,
      86,    72,    76,    91,    92,    34,    59,    24,    25,    26
};

/* YYTABLE[YYPACT[STATE-NUM]] -- What to do in state STATE-NUM.  If
   positive, shift that token.  If negative, reduce the rule whose
   number is the opposite.  If YYTABLE_NINF, syntax error.  */
static const yytype_int8 yytable[] =
{
      58,    -4,     1,    43,   -34,    27,    28,    33,    41,    42,
       2,     3,     4,     5,     6,     7,     8,     9,    10,    11,
      12,    13,    14,    15,    16,    17,    18,    19,    20,    21,
      29,    35,    30,    31,    22,    73,    32,    36,    44,    45,
      46,    51,    52,    53,    73,    54,    33,    33,    37,    38,
      39,    40,    47,    48,    55,    56,    49,    87,    93,    50,
      87,    56,    63,    64,    65,    60,    93,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    74,    77,    78,
      66,    22,    88,    89,     2,     3,     4,     5,     6,     7,
       8,     9,    10,    11,    12,    13,    14,    15,    16,    17,
      18,    19,    20,    21,    80,    82,    83,    90,    22,    94,
      97,   100,     2,     3,     4,     5,     6,     7,     8,     9,
      10,    11,    12,    13,    14,    15,    16,    17,    18,    19,
      20,    21,    57,    98,    99,    84,    22,    96,    81,    95,
      88,    89,     2,     3,     4,     5,     6,     7,     8,     9,
      10,    11,    12,    13,    14,    15,    16,    17,    18,    19,
      20,    21,    79,   101,     0,    90,    22,     2,     3,     4,
       5,     6,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    62,     0,     0,
      84,    22,     2,     3,     4,     5,     6,     7,     8,     9,
      10,    11,    12,    13,    14,    15,    16,    17,    18,    19,
      20,    21,     0,     0,     0,     0,    22
};

static const yytype_int8 yycheck[] =
{
      25,     0,     1,    31,     3,    29,    30,    35,    29,    30,
       9,    10,    11,    12,    13,    14,    15,    16,    17,    18,
      19,    20,    21,    22,    23,    24,    25,    26,    27,    28,
      30,     8,    30,    30,    33,    60,    31,    31,    15,    16,
      17,    29,    30,    31,    69,    22,    35,    35,    31,    31,
      31,    29,    31,    29,     0,     3,    31,    82,    83,    31,
      85,     3,     4,     5,     6,    35,    91,     9,    10,    11,
      12,    13,    14,    15,    16,    17,    18,    19,    20,    21,
      22,    23,    24,    25,    26,    27,    28,    36,    29,    29,
      32,    33,     7,     8,     9,    10,    11,    12,    13,    14,
      15,    16,    17,    18,    19,    20,    21,    22,    23,    24,
      25,    26,    27,    28,    36,    35,    35,    32,    33,    29,
      29,    36,     9,    10,    11,    12,    13,    14,    15,    16,
      17,    18,    19,    20,    21,    22,    23,    24,    25,    26,
      27,    28,    24,    29,    29,    32,    33,    85,    69,    36,
       7,     8,     9,    10,    11,    12,    13,    14,    15,    16,
      17,    18,    19,    20,    21,    22,    23,    24,    25,    26,
      27,    28,    67,    91,    -1,    32,    33,     9,    10,    11,
      12,    13,    14,    15,    16,    17,    18,    19,    20,    21,
      22,    23,    24,    25,    26,    27,    28,    59,    -1,    -1,
      32,    33,     9,    10,    11,    12,    13,    14,    15,    16,
      17,    18,    19,    20,    21,    22,    23,    24,    25,    26,
      27,    28,    -1,    -1,    -1,    -1,    33
};

/* YYSTOS[STATE-NUM] -- The symbol kind of the accessing symbol of
   state STATE-NUM.  */
static const yytype_int8 yystos[] =
{
       0,     1,     9,    10,    11,    12,    13,    14,    15,    16,
      17,    18,    19,    20,    21,    22,    23,    24,    25,    26,
      27,    28,    33,    38,    54,    55,    56,    29,    30,    30,
      30,    30,    31,    35,    52,    52,    31,    31,    31,    31,
      29,    29,    30,    31,    52,    52,    52,    31,    29,    31,
      31,    29,    30,    31,    52,     0,     3,    39,    56,    53,
      35,    40,    54,     4,     5,     6,    32,    39,    41,    42,
      43,    44,    48,    56,    36,    45,    49,    29,    29,    40,
      36,    43,    35,    35,    32,    46,    47,    56,     7,     8,
      32,    50,    51,    56,    29,    36,    47,    29,    29,    29,
      36,    51
};

/* YYR1[RULE-NUM] -- Symbol kind of the left-hand side of rule RULE-NUM.  */
static const yytype_int8 yyr1[] =
{
       0,    37,    38,    38,    38,    39,    40,    41,    41,    42,
      42,    43,    43,    43,    43,    43,    43,    45,    44,    46,
      46,    47,    47,    49,    48,    50,    50,    51,    51,    51,
      51,    53,    52,    54,    54,    55,    55,    56,    56,    56,
      56,    56,    56,    56,    56,    56,    56,    56,    56,    56,
      56,    56,    56,    56,    56,    56,    56,    56,    56,    56,
      56,    56,    56,    56
};

/* YYR2[RULE-NUM] -- Number of symbols on the right-hand side of rule RULE-NUM.  */
static const yytype_int8 yyr2[] =
{
       0,     2,     3,     1,     0,     1,     3,     1,     0,     2,
       1,     1,     1,     2,     2,     2,     1,     0,     5,     2,
       1,     2,     1,     0,     5,     2,     1,     2,     2,     2,
       1,     0,     4,     1,     0,     2,     1,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2,     2,     2,     2,     2,     2,     2,
       2,     2,     2,     2
};


enum { YYENOMEM = -2 };

#define yyerrok         (yyerrstatus = 0)
#define yyclearin       (yychar = GMLEMPTY)

#define YYACCEPT        goto yyacceptlab
#define YYABORT         goto yyabortlab
#define YYERROR         goto yyerrorlab
#define YYNOMEM         goto yyexhaustedlab


#define YYRECOVERING()  (!!yyerrstatus)

#define YYBACKUP(Token, Value)                                    \
  do                                                              \
    if (yychar == GMLEMPTY)                                        \
      {                                                           \
        yychar = (Token);                                         \
        yylval = (Value);                                         \
        YYPOPSTACK (yylen);                                       \
        yystate = *yyssp;                                         \
        goto yybackup;                                            \
      }                                                           \
    else                                                          \
      {                                                           \
        yyerror (YY_("syntax error: cannot back up")); \
        YYERROR;                                                  \
      }                                                           \
  while (0)

/* Backward compatibility with an undocumented macro.
   Use GMLerror or GMLUNDEF. */
#define YYERRCODE GMLUNDEF


/* Enable debugging if requested.  */
#if GMLDEBUG

# ifndef YYFPRINTF
#  include <stdio.h> /* INFRINGES ON USER NAME SPACE */
#  define YYFPRINTF fprintf
# endif

# define YYDPRINTF(Args)                        \
do {                                            \
  if (yydebug)                                  \
    YYFPRINTF Args;                             \
} while (0)




# define YY_SYMBOL_PRINT(Title, Kind, Value, Location)                    \
do {                                                                      \
  if (yydebug)                                                            \
    {                                                                     \
      YYFPRINTF (stderr, "%s ", Title);                                   \
      yy_symbol_print (stderr,                                            \
                  Kind, Value); \
      YYFPRINTF (stderr, "\n");                                           \
    }                                                                     \
} while (0)


/*-----------------------------------.
| Print this symbol's value on YYO.  |
`-----------------------------------*/

static void
yy_symbol_value_print (FILE *yyo,
                       yysymbol_kind_t yykind, YYSTYPE const * const yyvaluep)
{
  FILE *yyoutput = yyo;
  YY_USE (yyoutput);
  if (!yyvaluep)
    return;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YY_USE (yykind);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/*---------------------------.
| Print this symbol on YYO.  |
`---------------------------*/

static void
yy_symbol_print (FILE *yyo,
                 yysymbol_kind_t yykind, YYSTYPE const * const yyvaluep)
{
  YYFPRINTF (yyo, "%s %s (",
             yykind < YYNTOKENS ? "token" : "nterm", yysymbol_name (yykind));

  yy_symbol_value_print (yyo, yykind, yyvaluep);
  YYFPRINTF (yyo, ")");
}

/*------------------------------------------------------------------.
| yy_stack_print -- Print the state stack from its BOTTOM up to its |
| TOP (included).                                                   |
`------------------------------------------------------------------*/

static void
yy_stack_print (yy_state_t *yybottom, yy_state_t *yytop)
{
  YYFPRINTF (stderr, "Stack now");
  for (; yybottom <= yytop; yybottom++)
    {
      int yybot = *yybottom;
      YYFPRINTF (stderr, " %d", yybot);
    }
  YYFPRINTF (stderr, "\n");
}

# define YY_STACK_PRINT(Bottom, Top)                            \
do {                                                            \
  if (yydebug)                                                  \
    yy_stack_print ((Bottom), (Top));                           \
} while (0)


/*------------------------------------------------.
| Report that the YYRULE is going to be reduced.  |
`------------------------------------------------*/

static void
yy_reduce_print (yy_state_t *yyssp, YYSTYPE *yyvsp,
                 int yyrule)
{
  int yylno = yyrline[yyrule];
  int yynrhs = yyr2[yyrule];
  int yyi;
  YYFPRINTF (stderr, "Reducing stack by rule %d (line %d):\n",
             yyrule - 1, yylno);
  /* The symbols being reduced.  */
  for (yyi = 0; yyi < yynrhs; yyi++)
    {
      YYFPRINTF (stderr, "   $%d = ", yyi + 1);
      yy_symbol_print (stderr,
                       YY_ACCESSING_SYMBOL (+yyssp[yyi + 1 - yynrhs]),
                       &yyvsp[(yyi + 1) - (yynrhs)]);
      YYFPRINTF (stderr, "\n");
    }
}

# define YY_REDUCE_PRINT(Rule)          \
do {                                    \
  if (yydebug)                          \
    yy_reduce_print (yyssp, yyvsp, Rule); \
} while (0)

/* Nonzero means print parse trace.  It is left uninitialized so that
   multiple parsers can coexist.  */
int yydebug;
#else /* !GMLDEBUG */
# define YYDPRINTF(Args) ((void) 0)
# define YY_SYMBOL_PRINT(Title, Kind, Value, Location)
# define YY_STACK_PRINT(Bottom, Top)
# define YY_REDUCE_PRINT(Rule)
#endif /* !GMLDEBUG */


/* YYINITDEPTH -- initial size of the parser's stacks.  */
#ifndef YYINITDEPTH
# define YYINITDEPTH 200
#endif

/* YYMAXDEPTH -- maximum size the stacks can grow to (effective only
   if the built-in stack extension method is used).

   Do not make this value too large; the results are undefined if
   YYSTACK_ALLOC_MAXIMUM < YYSTACK_BYTES (YYMAXDEPTH)
   evaluated with infinite-precision integer arithmetic.  */

#ifndef YYMAXDEPTH
# define YYMAXDEPTH 10000
#endif






/*-----------------------------------------------.
| Release the memory associated to this symbol.  |
`-----------------------------------------------*/

static void
yydestruct (const char *yymsg,
            yysymbol_kind_t yykind, YYSTYPE *yyvaluep)
{
  YY_USE (yyvaluep);
  if (!yymsg)
    yymsg = "Deleting";
  YY_SYMBOL_PRINT (yymsg, yykind, yyvaluep, yylocationp);

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  YY_USE (yykind);
  YY_IGNORE_MAYBE_UNINITIALIZED_END
}


/* Lookahead token kind.  */
int yychar;

/* The semantic value of the lookahead symbol.  */
YYSTYPE yylval;
/* Number of syntax errors so far.  */
int yynerrs;




/*----------.
| yyparse.  |
`----------*/

int
yyparse (void)
{
    yy_state_fast_t yystate = 0;
    /* Number of tokens to shift before error messages enabled.  */
    int yyerrstatus = 0;

    /* Refer to the stacks through separate pointers, to allow yyoverflow
       to reallocate them elsewhere.  */

    /* Their size.  */
    YYPTRDIFF_T yystacksize = YYINITDEPTH;

    /* The state stack: array, bottom, top.  */
    yy_state_t yyssa[YYINITDEPTH];
    yy_state_t *yyss = yyssa;
    yy_state_t *yyssp = yyss;

    /* The semantic value stack: array, bottom, top.  */
    YYSTYPE yyvsa[YYINITDEPTH];
    YYSTYPE *yyvs = yyvsa;
    YYSTYPE *yyvsp = yyvs;

  int yyn;
  /* The return value of yyparse.  */
  int yyresult;
  /* Lookahead symbol kind.  */
  yysymbol_kind_t yytoken = YYSYMBOL_YYEMPTY;
  /* The variables used to return semantic value and location from the
     action routines.  */
  YYSTYPE yyval;



#define YYPOPSTACK(N)   (yyvsp -= (N), yyssp -= (N))

  /* The number of symbols on the RHS of the reduced rule.
     Keep to zero when no symbol should be popped.  */
  int yylen = 0;

  YYDPRINTF ((stderr, "Starting parse\n"));

  yychar = GMLEMPTY; /* Cause a token to be read.  */

  goto yysetstate;


/*------------------------------------------------------------.
| yynewstate -- push a new state, which is found in yystate.  |
`------------------------------------------------------------*/
yynewstate:
  /* In all cases, when you get here, the value and location stacks
     have just been pushed.  So pushing a state here evens the stacks.  */
  yyssp++;


/*--------------------------------------------------------------------.
| yysetstate -- set current state (the top of the stack) to yystate.  |
`--------------------------------------------------------------------*/
yysetstate:
  YYDPRINTF ((stderr, "Entering state %d\n", yystate));
  YY_ASSERT (0 <= yystate && yystate < YYNSTATES);
  YY_IGNORE_USELESS_CAST_BEGIN
  *yyssp = YY_CAST (yy_state_t, yystate);
  YY_IGNORE_USELESS_CAST_END
  YY_STACK_PRINT (yyss, yyssp);

  if (yyss + yystacksize - 1 <= yyssp)
#if !defined yyoverflow && !defined YYSTACK_RELOCATE
    YYNOMEM;
#else
    {
      /* Get the current used size of the three stacks, in elements.  */
      YYPTRDIFF_T yysize = yyssp - yyss + 1;

# if defined yyoverflow
      {
        /* Give user a chance to reallocate the stack.  Use copies of
           these so that the &'s don't force the real ones into
           memory.  */
        yy_state_t *yyss1 = yyss;
        YYSTYPE *yyvs1 = yyvs;

        /* Each stack pointer address is followed by the size of the
           data in use in that stack, in bytes.  This used to be a
           conditional around just the two extra args, but that might
           be undefined if yyoverflow is a macro.  */
        yyoverflow (YY_("memory exhausted"),
                    &yyss1, yysize * YYSIZEOF (*yyssp),
                    &yyvs1, yysize * YYSIZEOF (*yyvsp),
                    &yystacksize);
        yyss = yyss1;
        yyvs = yyvs1;
      }
# else /* defined YYSTACK_RELOCATE */
      /* Extend the stack our own way.  */
      if (YYMAXDEPTH <= yystacksize)
        YYNOMEM;
      yystacksize *= 2;
      if (YYMAXDEPTH < yystacksize)
        yystacksize = YYMAXDEPTH;

      {
        yy_state_t *yyss1 = yyss;
        union yyalloc *yyptr =
          YY_CAST (union yyalloc *,
                   YYSTACK_ALLOC (YY_CAST (YYSIZE_T, YYSTACK_BYTES (yystacksize))));
        if (! yyptr)
          YYNOMEM;
        YYSTACK_RELOCATE (yyss_alloc, yyss);
        YYSTACK_RELOCATE (yyvs_alloc, yyvs);
#  undef YYSTACK_RELOCATE
        if (yyss1 != yyssa)
          YYSTACK_FREE (yyss1);
      }
# endif

      yyssp = yyss + yysize - 1;
      yyvsp = yyvs + yysize - 1;

      YY_IGNORE_USELESS_CAST_BEGIN
      YYDPRINTF ((stderr, "Stack size increased to %ld\n",
                  YY_CAST (long, yystacksize)));
      YY_IGNORE_USELESS_CAST_END

      if (yyss + yystacksize - 1 <= yyssp)
        YYABORT;
    }
#endif /* !defined yyoverflow && !defined YYSTACK_RELOCATE */


  if (yystate == YYFINAL)
    YYACCEPT;

  goto yybackup;


/*-----------.
| yybackup.  |
`-----------*/
yybackup:
  /* Do appropriate processing given the current state.  Read a
     lookahead token if we need one and don't already have one.  */

  /* First try to decide what to do without reference to lookahead token.  */
  yyn = yypact[yystate];
  if (yypact_value_is_default (yyn))
    goto yydefault;

  /* Not known => get a lookahead token if don't already have one.  */

  /* YYCHAR is either empty, or end-of-input, or a valid lookahead.  */
  if (yychar == GMLEMPTY)
    {
      YYDPRINTF ((stderr, "Reading a token\n"));
      yychar = yylex ();
    }

  if (yychar <= GMLEOF)
    {
      yychar = GMLEOF;
      yytoken = YYSYMBOL_YYEOF;
      YYDPRINTF ((stderr, "Now at end of input.\n"));
    }
  else if (yychar == GMLerror)
    {
      /* The scanner already issued an error message, process directly
         to error recovery.  But do not keep the error token as
         lookahead, it is too special and may lead us to an endless
         loop in error recovery. */
      yychar = GMLUNDEF;
      yytoken = YYSYMBOL_YYerror;
      goto yyerrlab1;
    }
  else
    {
      yytoken = YYTRANSLATE (yychar);
      YY_SYMBOL_PRINT ("Next token is", yytoken, &yylval, &yylloc);
    }

  /* If the proper action on seeing token YYTOKEN is to reduce or to
     detect an error, take that action.  */
  yyn += yytoken;
  if (yyn < 0 || YYLAST < yyn || yycheck[yyn] != yytoken)
    goto yydefault;
  yyn = yytable[yyn];
  if (yyn <= 0)
    {
      if (yytable_value_is_error (yyn))
        goto yyerrlab;
      yyn = -yyn;
      goto yyreduce;
    }

  /* Count tokens shifted since error; after three, turn off error
     status.  */
  if (yyerrstatus)
    yyerrstatus--;

  /* Shift the lookahead token.  */
  YY_SYMBOL_PRINT ("Shifting", yytoken, &yylval, &yylloc);
  yystate = yyn;
  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END

  /* Discard the shifted token.  */
  yychar = GMLEMPTY;
  goto yynewstate;


/*-----------------------------------------------------------.
| yydefault -- do the default action for the current state.  |
`-----------------------------------------------------------*/
yydefault:
  yyn = yydefact[yystate];
  if (yyn == 0)
    goto yyerrlab;
  goto yyreduce;


/*-----------------------------.
| yyreduce -- do a reduction.  |
`-----------------------------*/
yyreduce:
  /* yyn is the number of a rule to reduce with.  */
  yylen = yyr2[yyn];

  /* If YYLEN is nonzero, implement the default value of the action:
     '$$ = $1'.

     Otherwise, the following line sets YYVAL to garbage.
     This behavior is undocumented and Bison
     users should not rely upon it.  Assigning to YYVAL
     unconditionally makes the parser a bit smaller, and it avoids a
     GCC warning that YYVAL may be used uninitialized.  */
  yyval = yyvsp[1-yylen];


  YY_REDUCE_PRINT (yyn);
  switch (yyn)
    {
  case 2: /* graph: optalist hdr body  */
#line 224 "../../cmd/tools/gmlparse.y"
                           {gmllexeof(); if (G->parent) popG(); }
#line 1395 "gmlparse.c"
    break;

  case 3: /* graph: error  */
#line 225 "../../cmd/tools/gmlparse.y"
              { cleanup(); YYABORT; }
#line 1401 "gmlparse.c"
    break;

  case 5: /* hdr: GRAPH  */
#line 229 "../../cmd/tools/gmlparse.y"
              { pushG(); }
#line 1407 "gmlparse.c"
    break;

  case 11: /* glistitem: node  */
#line 243 "../../cmd/tools/gmlparse.y"
                 { LIST_APPEND(&G->nodelist, (yyvsp[0].np)); }
#line 1413 "gmlparse.c"
    break;

  case 12: /* glistitem: edge  */
#line 244 "../../cmd/tools/gmlparse.y"
                 { LIST_APPEND(&G->edgelist, (yyvsp[0].ep)); }
#line 1419 "gmlparse.c"
    break;

  case 14: /* glistitem: DIRECTED INTEGER  */
#line 246 "../../cmd/tools/gmlparse.y"
                             { 
		if (setDir((yyvsp[0].str))) { 
		    yyerror("mixed directed and undirected graphs"); 
		    cleanup ();
		    YYABORT;
		}
	  }
#line 1431 "gmlparse.c"
    break;

  case 15: /* glistitem: ID INTEGER  */
#line 253 "../../cmd/tools/gmlparse.y"
                       { LIST_APPEND(&G->attrlist, mkAttr(gv_strdup("id"), 0, INTEGER, (yyvsp[0].str), 0)); }
#line 1437 "gmlparse.c"
    break;

  case 16: /* glistitem: alistitem  */
#line 254 "../../cmd/tools/gmlparse.y"
                      { LIST_APPEND(&G->attrlist, (yyvsp[0].ap)); }
#line 1443 "gmlparse.c"
    break;

  case 17: /* $@1: %empty  */
#line 257 "../../cmd/tools/gmlparse.y"
             { N = mkNode(); }
#line 1449 "gmlparse.c"
    break;

  case 18: /* node: NODE $@1 '[' nlist ']'  */
#line 257 "../../cmd/tools/gmlparse.y"
                                             { (yyval.np) = N; N = NULL; }
#line 1455 "gmlparse.c"
    break;

  case 21: /* nlistitem: ID INTEGER  */
#line 264 "../../cmd/tools/gmlparse.y"
                       { N->id = (yyvsp[0].str); }
#line 1461 "gmlparse.c"
    break;

  case 22: /* nlistitem: alistitem  */
#line 265 "../../cmd/tools/gmlparse.y"
                      { LIST_APPEND(&N->attrlist, (yyvsp[0].ap)); }
#line 1467 "gmlparse.c"
    break;

  case 23: /* $@2: %empty  */
#line 268 "../../cmd/tools/gmlparse.y"
             { E = mkEdge(); }
#line 1473 "gmlparse.c"
    break;

  case 24: /* edge: EDGE $@2 '[' elist ']'  */
#line 268 "../../cmd/tools/gmlparse.y"
                                             { (yyval.ep) = E; E = NULL; }
#line 1479 "gmlparse.c"
    break;

  case 27: /* elistitem: SOURCE INTEGER  */
#line 275 "../../cmd/tools/gmlparse.y"
                           { E->source = (yyvsp[0].str); }
#line 1485 "gmlparse.c"
    break;

  case 28: /* elistitem: TARGET INTEGER  */
#line 276 "../../cmd/tools/gmlparse.y"
                           { E->target = (yyvsp[0].str); }
#line 1491 "gmlparse.c"
    break;

  case 29: /* elistitem: ID INTEGER  */
#line 277 "../../cmd/tools/gmlparse.y"
                       { LIST_APPEND(&E->attrlist, mkAttr(gv_strdup("id"), 0, INTEGER, (yyvsp[0].str), 0)); }
#line 1497 "gmlparse.c"
    break;

  case 30: /* elistitem: alistitem  */
#line 278 "../../cmd/tools/gmlparse.y"
                      { LIST_APPEND(&E->attrlist, (yyvsp[0].ap)); }
#line 1503 "gmlparse.c"
    break;

  case 31: /* $@3: %empty  */
#line 281 "../../cmd/tools/gmlparse.y"
                {pushAlist(); }
#line 1509 "gmlparse.c"
    break;

  case 32: /* attrlist: '[' $@3 optalist ']'  */
#line 281 "../../cmd/tools/gmlparse.y"
                                             { (yyval.list) = popAlist(); }
#line 1515 "gmlparse.c"
    break;

  case 35: /* alist: alist alistitem  */
#line 288 "../../cmd/tools/gmlparse.y"
                          { LIST_APPEND(L, (yyvsp[0].ap)); }
#line 1521 "gmlparse.c"
    break;

  case 36: /* alist: alistitem  */
#line 289 "../../cmd/tools/gmlparse.y"
                    { LIST_APPEND(L, (yyvsp[0].ap)); }
#line 1527 "gmlparse.c"
    break;

  case 37: /* alistitem: NAME INTEGER  */
#line 292 "../../cmd/tools/gmlparse.y"
                         { (yyval.ap) = mkAttr ((yyvsp[-1].str), 0, INTEGER, (yyvsp[0].str), 0); }
#line 1533 "gmlparse.c"
    break;

  case 38: /* alistitem: NAME REAL  */
#line 293 "../../cmd/tools/gmlparse.y"
                         { (yyval.ap) = mkAttr ((yyvsp[-1].str), 0, REAL, (yyvsp[0].str), 0); }
#line 1539 "gmlparse.c"
    break;

  case 39: /* alistitem: NAME STRING  */
#line 294 "../../cmd/tools/gmlparse.y"
                         { (yyval.ap) = mkAttr ((yyvsp[-1].str), 0, STRING, (yyvsp[0].str), 0); }
#line 1545 "gmlparse.c"
    break;

  case 40: /* alistitem: NAME attrlist  */
#line 295 "../../cmd/tools/gmlparse.y"
                           { (yyval.ap) = mkAttr ((yyvsp[-1].str), 0, GML_LIST, 0, (yyvsp[0].list)); }
#line 1551 "gmlparse.c"
    break;

  case 41: /* alistitem: XVAL REAL  */
#line 296 "../../cmd/tools/gmlparse.y"
                       { (yyval.ap) = mkAttr (0, XVAL, REAL, (yyvsp[0].str), 0); }
#line 1557 "gmlparse.c"
    break;

  case 42: /* alistitem: XVAL INTEGER  */
#line 297 "../../cmd/tools/gmlparse.y"
                          { (yyval.ap) = mkAttr (0, XVAL, REAL, (yyvsp[0].str), 0); }
#line 1563 "gmlparse.c"
    break;

  case 43: /* alistitem: YVAL REAL  */
#line 298 "../../cmd/tools/gmlparse.y"
                       { (yyval.ap) = mkAttr (0, YVAL, REAL, (yyvsp[0].str), 0); }
#line 1569 "gmlparse.c"
    break;

  case 44: /* alistitem: WVAL REAL  */
#line 299 "../../cmd/tools/gmlparse.y"
                       { (yyval.ap) = mkAttr (0, WVAL, REAL, (yyvsp[0].str), 0); }
#line 1575 "gmlparse.c"
    break;

  case 45: /* alistitem: HVAL REAL  */
#line 300 "../../cmd/tools/gmlparse.y"
                       { (yyval.ap) = mkAttr (0, HVAL, REAL, (yyvsp[0].str), 0); }
#line 1581 "gmlparse.c"
    break;

  case 46: /* alistitem: LABEL STRING  */
#line 301 "../../cmd/tools/gmlparse.y"
                          { (yyval.ap) = mkAttr (0, LABEL, STRING, (yyvsp[0].str), 0); }
#line 1587 "gmlparse.c"
    break;

  case 47: /* alistitem: GRAPHICS attrlist  */
#line 302 "../../cmd/tools/gmlparse.y"
                               { (yyval.ap) = mkAttr (0, GRAPHICS, GML_LIST, 0, (yyvsp[0].list)); }
#line 1593 "gmlparse.c"
    break;

  case 48: /* alistitem: LABELGRAPHICS attrlist  */
#line 303 "../../cmd/tools/gmlparse.y"
                                    { (yyval.ap) = mkAttr (0, LABELGRAPHICS, GML_LIST, 0, (yyvsp[0].list)); }
#line 1599 "gmlparse.c"
    break;

  case 49: /* alistitem: TYPE STRING  */
#line 304 "../../cmd/tools/gmlparse.y"
                         { (yyval.ap) = mkAttr (0, TYPE, STRING, (yyvsp[0].str), 0); }
#line 1605 "gmlparse.c"
    break;

  case 50: /* alistitem: FILL STRING  */
#line 305 "../../cmd/tools/gmlparse.y"
                         { (yyval.ap) = mkAttr (0, FILL, STRING, (yyvsp[0].str), 0); }
#line 1611 "gmlparse.c"
    break;

  case 51: /* alistitem: OUTLINE STRING  */
#line 306 "../../cmd/tools/gmlparse.y"
                            { (yyval.ap) = mkAttr (0, OUTLINE, STRING, (yyvsp[0].str), 0); }
#line 1617 "gmlparse.c"
    break;

  case 52: /* alistitem: OUTLINESTYLE STRING  */
#line 307 "../../cmd/tools/gmlparse.y"
                                 { (yyval.ap) = mkAttr (0, OUTLINESTYLE, STRING, (yyvsp[0].str), 0); }
#line 1623 "gmlparse.c"
    break;

  case 53: /* alistitem: OUTLINEWIDTH INTEGER  */
#line 308 "../../cmd/tools/gmlparse.y"
                                  { (yyval.ap) = mkAttr (0, OUTLINEWIDTH, INTEGER, (yyvsp[0].str), 0); }
#line 1629 "gmlparse.c"
    break;

  case 54: /* alistitem: WIDTH REAL  */
#line 309 "../../cmd/tools/gmlparse.y"
                        { (yyval.ap) = mkAttr (0, WIDTH, REAL, (yyvsp[0].str), 0); }
#line 1635 "gmlparse.c"
    break;

  case 55: /* alistitem: WIDTH INTEGER  */
#line 310 "../../cmd/tools/gmlparse.y"
                           { (yyval.ap) = mkAttr (0, WIDTH, INTEGER, (yyvsp[0].str), 0); }
#line 1641 "gmlparse.c"
    break;

  case 56: /* alistitem: STYLE STRING  */
#line 311 "../../cmd/tools/gmlparse.y"
                          { (yyval.ap) = mkAttr (0, STYLE, STRING, (yyvsp[0].str), 0); }
#line 1647 "gmlparse.c"
    break;

  case 57: /* alistitem: STYLE attrlist  */
#line 312 "../../cmd/tools/gmlparse.y"
                            { (yyval.ap) = mkAttr (0, STYLE, GML_LIST, 0, (yyvsp[0].list)); }
#line 1653 "gmlparse.c"
    break;

  case 58: /* alistitem: LINE attrlist  */
#line 313 "../../cmd/tools/gmlparse.y"
                           { (yyval.ap) = mkAttr (0, LINE, GML_LIST, 0, (yyvsp[0].list)); }
#line 1659 "gmlparse.c"
    break;

  case 59: /* alistitem: POINT attrlist  */
#line 314 "../../cmd/tools/gmlparse.y"
                            { (yyval.ap) = mkAttr (0, POINT, GML_LIST, 0, (yyvsp[0].list)); }
#line 1665 "gmlparse.c"
    break;

  case 60: /* alistitem: TEXT STRING  */
#line 315 "../../cmd/tools/gmlparse.y"
                         { (yyval.ap) = mkAttr (0, TEXT, STRING, (yyvsp[0].str), 0); }
#line 1671 "gmlparse.c"
    break;

  case 61: /* alistitem: FONTNAME STRING  */
#line 316 "../../cmd/tools/gmlparse.y"
                             { (yyval.ap) = mkAttr (0, FONTNAME, STRING, (yyvsp[0].str), 0); }
#line 1677 "gmlparse.c"
    break;

  case 62: /* alistitem: FONTSIZE INTEGER  */
#line 317 "../../cmd/tools/gmlparse.y"
                              { (yyval.ap) = mkAttr (0, FONTNAME, INTEGER, (yyvsp[0].str), 0); }
#line 1683 "gmlparse.c"
    break;

  case 63: /* alistitem: COLOR STRING  */
#line 318 "../../cmd/tools/gmlparse.y"
                          { (yyval.ap) = mkAttr (0, COLOR, STRING, (yyvsp[0].str), 0); }
#line 1689 "gmlparse.c"
    break;


#line 1693 "gmlparse.c"

      default: break;
    }
  /* User semantic actions sometimes alter yychar, and that requires
     that yytoken be updated with the new translation.  We take the
     approach of translating immediately before every use of yytoken.
     One alternative is translating here after every semantic action,
     but that translation would be missed if the semantic action invokes
     YYABORT, YYACCEPT, or YYERROR immediately after altering yychar or
     if it invokes YYBACKUP.  In the case of YYABORT or YYACCEPT, an
     incorrect destructor might then be invoked immediately.  In the
     case of YYERROR or YYBACKUP, subsequent parser actions might lead
     to an incorrect destructor call or verbose syntax error message
     before the lookahead is translated.  */
  YY_SYMBOL_PRINT ("-> $$ =", YY_CAST (yysymbol_kind_t, yyr1[yyn]), &yyval, &yyloc);

  YYPOPSTACK (yylen);
  yylen = 0;

  *++yyvsp = yyval;

  /* Now 'shift' the result of the reduction.  Determine what state
     that goes to, based on the state we popped back to and the rule
     number reduced by.  */
  {
    const int yylhs = yyr1[yyn] - YYNTOKENS;
    const int yyi = yypgoto[yylhs] + *yyssp;
    yystate = (0 <= yyi && yyi <= YYLAST && yycheck[yyi] == *yyssp
               ? yytable[yyi]
               : yydefgoto[yylhs]);
  }

  goto yynewstate;


/*--------------------------------------.
| yyerrlab -- here on detecting error.  |
`--------------------------------------*/
yyerrlab:
  /* Make sure we have latest lookahead translation.  See comments at
     user semantic actions for why this is necessary.  */
  yytoken = yychar == GMLEMPTY ? YYSYMBOL_YYEMPTY : YYTRANSLATE (yychar);
  /* If not already recovering from an error, report this error.  */
  if (!yyerrstatus)
    {
      ++yynerrs;
      yyerror (YY_("syntax error"));
    }

  if (yyerrstatus == 3)
    {
      /* If just tried and failed to reuse lookahead token after an
         error, discard it.  */

      if (yychar <= GMLEOF)
        {
          /* Return failure if at end of input.  */
          if (yychar == GMLEOF)
            YYABORT;
        }
      else
        {
          yydestruct ("Error: discarding",
                      yytoken, &yylval);
          yychar = GMLEMPTY;
        }
    }

  /* Else will try to reuse lookahead token after shifting the error
     token.  */
  goto yyerrlab1;


/*---------------------------------------------------.
| yyerrorlab -- error raised explicitly by YYERROR.  |
`---------------------------------------------------*/
yyerrorlab:
  /* Pacify compilers when the user code never invokes YYERROR and the
     label yyerrorlab therefore never appears in user code.  */
  if (0)
    YYERROR;
  ++yynerrs;

  /* Do not reclaim the symbols of the rule whose action triggered
     this YYERROR.  */
  YYPOPSTACK (yylen);
  yylen = 0;
  YY_STACK_PRINT (yyss, yyssp);
  yystate = *yyssp;
  goto yyerrlab1;


/*-------------------------------------------------------------.
| yyerrlab1 -- common code for both syntax error and YYERROR.  |
`-------------------------------------------------------------*/
yyerrlab1:
  yyerrstatus = 3;      /* Each real token shifted decrements this.  */

  /* Pop stack until we find a state that shifts the error token.  */
  for (;;)
    {
      yyn = yypact[yystate];
      if (!yypact_value_is_default (yyn))
        {
          yyn += YYSYMBOL_YYerror;
          if (0 <= yyn && yyn <= YYLAST && yycheck[yyn] == YYSYMBOL_YYerror)
            {
              yyn = yytable[yyn];
              if (0 < yyn)
                break;
            }
        }

      /* Pop the current state because it cannot handle the error token.  */
      if (yyssp == yyss)
        YYABORT;


      yydestruct ("Error: popping",
                  YY_ACCESSING_SYMBOL (yystate), yyvsp);
      YYPOPSTACK (1);
      yystate = *yyssp;
      YY_STACK_PRINT (yyss, yyssp);
    }

  YY_IGNORE_MAYBE_UNINITIALIZED_BEGIN
  *++yyvsp = yylval;
  YY_IGNORE_MAYBE_UNINITIALIZED_END


  /* Shift the error token.  */
  YY_SYMBOL_PRINT ("Shifting", YY_ACCESSING_SYMBOL (yyn), yyvsp, yylsp);

  yystate = yyn;
  goto yynewstate;


/*-------------------------------------.
| yyacceptlab -- YYACCEPT comes here.  |
`-------------------------------------*/
yyacceptlab:
  yyresult = 0;
  goto yyreturnlab;


/*-----------------------------------.
| yyabortlab -- YYABORT comes here.  |
`-----------------------------------*/
yyabortlab:
  yyresult = 1;
  goto yyreturnlab;


/*-----------------------------------------------------------.
| yyexhaustedlab -- YYNOMEM (memory exhaustion) comes here.  |
`-----------------------------------------------------------*/
yyexhaustedlab:
  yyerror (YY_("memory exhausted"));
  yyresult = 2;
  goto yyreturnlab;


/*----------------------------------------------------------.
| yyreturnlab -- parsing is finished, clean up and return.  |
`----------------------------------------------------------*/
yyreturnlab:
  if (yychar != GMLEMPTY)
    {
      /* Make sure we have latest lookahead translation.  See comments at
         user semantic actions for why this is necessary.  */
      yytoken = YYTRANSLATE (yychar);
      yydestruct ("Cleanup: discarding lookahead",
                  yytoken, &yylval);
    }
  /* Do not reclaim the symbols of the rule whose action triggered
     this YYABORT or YYACCEPT.  */
  YYPOPSTACK (yylen);
  YY_STACK_PRINT (yyss, yyssp);
  while (yyssp != yyss)
    {
      yydestruct ("Cleanup: popping",
                  YY_ACCESSING_SYMBOL (+*yyssp), yyvsp);
      YYPOPSTACK (1);
    }
#ifndef yyoverflow
  if (yyss != yyssa)
    YYSTACK_FREE (yyss);
#endif

  return yyresult;
}

#line 321 "../../cmd/tools/gmlparse.y"


static void free_attr(gmlattr *p) {
    if (!p) return;
    if (p->kind == GML_LIST && p->u.lp)
	free_attrs(p->u.lp);
    else
	free (p->u.value);
    free (p->name);
    free (p);
}

static void deparseList(attrs_t *alist, agxbuf *xb);

static void
deparseAttr (gmlattr* ap, agxbuf* xb)
{
    if (ap->kind == GML_LIST) {
	agxbprint (xb, "%s ", ap->name);
	deparseList (ap->u.lp, xb);
    }
    else if (ap->kind == STRING) {
	agxbprint (xb, "%s \"%s\"", ap->name, ap->u.value);
    }
    else {
	agxbprint (xb, "%s %s", ap->name, ap->u.value);
    }
}

static void deparseList(attrs_t *alist, agxbuf *xb) {
    agxbput (xb, "[ "); 
    for (size_t i = 0; alist != NULL && i < LIST_SIZE(alist); ++i) {
	gmlattr *const ap = LIST_GET(alist, i);
	deparseAttr (ap, xb);
	agxbputc (xb, ' ');
    }
    agxbput (xb, "]"); 
  
}

static void
unknown (Agobj_t* obj, gmlattr* ap, agxbuf* xb)
{
    char* str;

    if (ap->kind == GML_LIST) {
	deparseList (ap->u.lp, xb);
	str = agxbuse (xb);
    }
    else
	str = ap->u.value;

    agsafeset (obj, ap->name, str, "");
}

static void addNodeLabelGraphics(Agnode_t *np, attrs_t *alist, agxbuf *unk) {
    int cnt = 0;

    if (!alist)
	return;

    for (size_t i = 0; i < LIST_SIZE(alist); ++i) {
	gmlattr *const ap = LIST_GET(alist, i);
	if (ap->sort == TEXT) {
	    agsafeset (np, "label", ap->u.value, "");
	}
	else if (ap->sort == COLOR) {
	    agsafeset (np, "fontcolor", ap->u.value, "");
	}
	else if (ap->sort == FONTSIZE) {
	    agsafeset (np, "fontsize", ap->u.value, "");
	}
	else if (ap->sort == FONTNAME) {
	    agsafeset (np, "fontname", ap->u.value, "");
	}
	else {
	    if (cnt)
		agxbputc (unk, ' '); 
	    else {
		agxbput (unk, "[ "); 
	    }
	    deparseAttr (ap, unk);
	    cnt++;
	}
    }

    if (cnt) {
	agxbput (unk, " ]"); 
	agsafeset (np, "LabelGraphics", agxbuse (unk), "");
    }
    else
	agxbclear (unk); 
}

static void addEdgeLabelGraphics(Agedge_t *ep, attrs_t *alist, agxbuf *xb,
                                 agxbuf *unk) {
    char* x = "0";
    char* y = "0";
    int cnt = 0;

    if (!alist)
	return;

    for (size_t i = 0; i < LIST_SIZE(alist); ++i) {
	gmlattr *const ap = LIST_GET(alist, i);
	if (ap->sort == TEXT) {
	    agsafeset (ep, "label", ap->u.value, "");
	}
	else if (ap->sort == COLOR) {
	    agsafeset (ep, "fontcolor", ap->u.value, "");
	}
	else if (ap->sort == FONTSIZE) {
	    agsafeset (ep, "fontsize", ap->u.value, "");
	}
	else if (ap->sort == FONTNAME) {
	    agsafeset (ep, "fontname", ap->u.value, "");
	}
	else if (ap->sort == XVAL) {
	    x = ap->u.value;
	}
	else if (ap->sort == YVAL) {
	    y = ap->u.value;
	}
	else {
	    if (cnt)
		agxbputc (unk, ' '); 
	    else {
		agxbput (unk, "[ "); 
	    }
	    deparseAttr (ap, unk);
	    cnt++;
	}
    }

    agxbprint (xb, "%s,%s", x, y);
    agsafeset (ep, "lp", agxbuse (xb), "");

    if (cnt) {
	agxbput (unk, " ]"); 
	agsafeset (ep, "LabelGraphics", agxbuse (unk), "");
    }
    else
	agxbclear (unk); 
}

static void addNodeGraphics(Agnode_t *np, attrs_t *alist, agxbuf *xb,
                            agxbuf *unk) {
    char* x = "0";
    char* y = "0";
    char buf[BUFSIZ];
    double d;
    int cnt = 0;

    for (size_t i = 0; alist != NULL && i < LIST_SIZE(alist); ++i) {
	gmlattr *const ap = LIST_GET(alist, i);
	if (ap->sort == XVAL) {
	    x = ap->u.value;
	}
	else if (ap->sort == YVAL) {
	    y = ap->u.value;
	}
	else if (ap->sort == WVAL) {
	    d = atof (ap->u.value);
	    snprintf(buf, sizeof(buf), "%.04f", d/72.0);
	    agsafeset (np, "width", buf, "");
	}
	else if (ap->sort == HVAL) {
	    d = atof (ap->u.value);
	    snprintf(buf, sizeof(buf), "%.04f", d/72.0);
	    agsafeset (np, "height", buf, "");
	}
	else if (ap->sort == TYPE) {
	    agsafeset (np, "shape", ap->u.value, "");
	}
	else if (ap->sort == FILL) {
	    agsafeset (np, "color", ap->u.value, "");
	}
	else if (ap->sort == OUTLINE) {
	    agsafeset (np, "pencolor", ap->u.value, "");
	}
	else if (ap->sort == WIDTH || ap->sort == OUTLINEWIDTH) {
	    agsafeset (np, "penwidth", ap->u.value, "");
	}
	else if (ap->sort == STYLE || ap->sort == OUTLINESTYLE) {
	    agsafeset (np, "style", ap->u.value, "");
	}
	else {
	    if (cnt)
		agxbputc (unk, ' '); 
	    else {
		agxbput (unk, "[ "); 
	    }
	    deparseAttr (ap, unk);
	    cnt++;
	}
    }

    agxbprint (xb, "%s,%s", x, y);
    agsafeset (np, "pos", agxbuse (xb), "");

    if (cnt) {
	agxbput (unk, " ]"); 
	agsafeset (np, "graphics", agxbuse (unk), "");
    }
    else
	agxbclear (unk); 
}

static void addEdgePoint(Agedge_t *ep, attrs_t *alist, agxbuf *xb) {
    char* x = "0";
    char* y = "0";

    for (size_t i = 0; alist != NULL && i < LIST_SIZE(alist); ++i) {
        gmlattr *const ap = LIST_GET(alist, i);
        if (ap->sort == XVAL) {
	    x = ap->u.value;
	}
	else if (ap->sort == YVAL) {
	    y = ap->u.value;
	}
	else {
	    fprintf (stderr, "non-X/Y field in point attribute");
	    unknown ((Agobj_t*)ep, ap, xb);
	}
    }

    if (agxblen(xb)) agxbputc (xb, ' ');
    agxbprint (xb, "%s,%s", x, y);
}

static void addEdgePos(Agedge_t *ep, attrs_t *alist, agxbuf *xb) {
    if (!alist) return;
    for (size_t i = 0; i < LIST_SIZE(alist); ++i) {
	gmlattr *const ap = LIST_GET(alist, i);
	if (ap->sort == POINT) {
	    addEdgePoint (ep, ap->u.lp, xb);
	}
	else {
	    fprintf (stderr, "non-point field in line attribute");
	    unknown(&ep->base, ap, xb);
	}
    }
    agsafeset (ep, "pos", agxbuse (xb), "");
}

static void addEdgeGraphics(Agedge_t *ep, attrs_t *alist, agxbuf *xb,
                            agxbuf *unk) {
    int cnt = 0;

    for (size_t i = 0; alist != NULL && i < LIST_SIZE(alist); ++i) {
	gmlattr *const ap = LIST_GET(alist, i);
	if (ap->sort == WIDTH) {
	    agsafeset (ep, "penwidth", ap->u.value, "");
	}
	else if (ap->sort == STYLE) {
	    agsafeset (ep, "style", ap->u.value, "");
	}
	else if (ap->sort == FILL) {
	    agsafeset (ep, "color", ap->u.value, "");
	}
	else if (ap->sort == LINE) {
	    addEdgePos (ep, ap->u.lp, xb);
	}
	else {
	    if (cnt)
		agxbputc (unk, ' '); 
	    else {
		agxbput (unk, "[ "); 
	    }
	    deparseAttr (ap, unk);
	    cnt++;
	}
    }

    if (cnt) {
	agxbput (unk, " ]"); 
	agsafeset (ep, "graphics", agxbuse (unk), "");
    }
    else
	agxbclear(unk);
}

static void addAttrs(Agobj_t *obj, attrs_t *alist, agxbuf *xb, agxbuf *unk) {
    for (size_t i = 0; i < LIST_SIZE(alist); ++i) {
	gmlattr *const ap = LIST_GET(alist, i);
	if (ap->sort == GRAPHICS) {
	    if (AGTYPE(obj) == AGNODE)
		addNodeGraphics ((Agnode_t*)obj, ap->u.lp, xb, unk);
	    else if (AGTYPE(obj) == AGEDGE)
		addEdgeGraphics ((Agedge_t*)obj, ap->u.lp, xb, unk);
	    else
		unknown (obj, ap, xb);
	}
	else if (ap->sort == LABELGRAPHICS) {
	    if (AGTYPE(obj) == AGNODE)
		addNodeLabelGraphics ((Agnode_t*)obj, ap->u.lp, unk);
	    else if (AGTYPE(obj) == AGEDGE)
		addEdgeLabelGraphics ((Agedge_t*)obj, ap->u.lp, xb, unk);
	    else
		unknown (obj, ap, xb);
	}
	else
	    unknown (obj, ap, xb);
    }
}

static Agraph_t *mkGraph(gmlgraph *graph, Agraph_t *parent, char *name,
                         agxbuf *xb, agxbuf *unk) {
    Agraph_t* g;
    Agnode_t* n;
    Agnode_t* h;
    Agedge_t* e;

    if (parent) {
	g = agsubg (parent, NULL, 1);
    }
    else if (graph->directed >= 1)
	g = agopen (name, Agdirected, 0);
    else
	g = agopen (name, Agundirected, 0);

    if (!parent && L) {
	addAttrs(&g->base, L, xb, unk);
    } 
    for (size_t i = 0; i < LIST_SIZE(&graph->nodelist); ++i) {
	gmlnode *const np = LIST_GET(&graph->nodelist, i);
	if (!np->id) {
	   fprintf (stderr, "node without an id attribute"); 
	   graphviz_exit (1);
        }
	n = agnode (g, np->id, 1);
	addAttrs(&n->base, &np->attrlist, xb, unk);
    }

    for (size_t i = 0; i < LIST_SIZE(&graph->edgelist); ++i) {
	gmledge *ep = LIST_GET(&graph->edgelist, i);
	if (!ep->source) {
	   fprintf (stderr, "edge without an source attribute"); 
	   graphviz_exit (1);
        }
	if (!ep->target) {
	   fprintf (stderr, "node without an target attribute"); 
	   graphviz_exit (1);
        }
	n = agnode (g, ep->source, 1);
	h = agnode (g, ep->target, 1);
	e = agedge (g, n, h, NULL, 1);
	addAttrs(&e->base, &ep->attrlist, xb, unk);
    }
    for (size_t i = 0; i < LIST_SIZE(&graph->graphlist); ++i) {
	gmlgraph *const gp = LIST_GET(&graph->graphlist, i);
	mkGraph (gp, g, NULL, xb, unk);
    }

    addAttrs(&g->base, &graph->attrlist, xb, unk);

    return g;
}

Agraph_t*
gml_to_gv (char* name, FILE* fp, int cnt, int* errors)
{
    Agraph_t* g;
    int error;

    if (cnt == 0)
	initgmlscan(fp);
    else
	initgmlscan(0);
		
    L = NULL;
    pushAlist ();
    gmlparse ();

    error = gmlerrors();
    *errors |= error;
    if (!G || error)
	g = NULL;
    else {
	agxbuf xb = {0};
	agxbuf unk = {0};
	g = mkGraph (G, NULL, name, &xb, &unk);
	agxbfree (&xb);
	agxbfree(&unk);
    }

    cleanup ();

    return g;
}

static char *sortToStr(unsigned short sort) {
    char* s;

    switch (sort) {
    case GRAPH : 
	s = "graph"; break;
    case NODE : 
	s = "node"; break;
    case EDGE : 
	s = "edge"; break;
    case DIRECTED : 
	s = "directed"; break;
    case ID : 
	s = "id"; break;
    case SOURCE : 
	s = "source"; break;
    case TARGET : 
	s = "target"; break;
    case XVAL : 
	s = "xval"; break;
    case YVAL : 
	s = "yval"; break;
    case WVAL : 
	s = "wval"; break;
    case HVAL : 
	s = "hval"; break;
    case LABEL : 
	s = "label"; break;
    case GRAPHICS : 
	s = "graphics"; break;
    case LABELGRAPHICS : 
	s = "labelGraphics"; break;
    case TYPE : 
	s = "type"; break;
    case FILL : 
	s = "fill"; break;
    case OUTLINE : 
	s = "outline"; break;
    case OUTLINESTYLE : 
	s = "outlineStyle"; break;
    case OUTLINEWIDTH : 
	s = "outlineWidth"; break;
    case WIDTH : 
	s = "width"; break;
    case STYLE : 
	s = "style"; break;
    case LINE : 
	s = "line"; break;
    case POINT : 
	s = "point"; break;
    case TEXT : 
	s = "text"; break;
    case FONTSIZE : 
	s = "fontSize"; break;
    case FONTNAME : 
	s = "fontName"; break;
    case COLOR : 
	s = "color"; break;
    case INTEGER : 
	s = "integer"; break;
    case REAL : 
	s = "real"; break;
    case STRING : 
	s = "string"; break;
    case NAME : 
	s = "name"; break;
    case GML_LIST : 
	s = "list"; break;
    case '[' : 
	s = "["; break;
    case ']' : 
	s = "]"; break;
    default : 
	s = NULL;break;
    }

    return s;
}
