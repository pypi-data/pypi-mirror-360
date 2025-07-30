
#define GENERATE_ASDL_SEQ_CONSTRUCTOR(NAME, TYPE)                              \
  static asdl_##NAME##_seq *_Py_asdl_##NAME##_seq_new(Py_ssize_t size,         \
                                                      PyArena *arena) {        \
    asdl_##NAME##_seq *seq = NULL;                                             \
    size_t n;                                                                  \
    /* check size is sane */                                                   \
    if (size < 0 ||                                                            \
        (size && (((size_t)size - 1) > (SIZE_MAX / sizeof(void *))))) {        \
      PyErr_NoMemory();                                                        \
      return NULL;                                                             \
    }                                                                          \
    n = (size ? (sizeof(TYPE *) * (size - 1)) : 0);                            \
    /* check if size can be added safely */                                    \
    if (n > SIZE_MAX - sizeof(asdl_##NAME##_seq)) {                            \
      PyErr_NoMemory();                                                        \
      return NULL;                                                             \
    }                                                                          \
    n += sizeof(asdl_##NAME##_seq);                                            \
    seq = (asdl_##NAME##_seq *)_PyArena_Malloc(arena, n);                      \
    if (!seq) {                                                                \
      PyErr_NoMemory();                                                        \
      return NULL;                                                             \
    }                                                                          \
    memset(seq, 0, n);                                                         \
    seq->size = size;                                                          \
    seq->elements = (void **)seq->typed_elements;                              \
    return seq;                                                                \
  }

#define asdl_seq_SET(S, I, V) ((S)->typed_elements[(I)] = (V))
#define asdl_seq_SET_UNTYPED(S, I, V) ((S)->elements[(I)] = (V))

#define asdl_seq_GET_UNTYPED(S, I) ((S)->elements[(I)])
#define asdl_seq_GET(S, I) ((S)->typed_elements[(I)])
#define asdl_seq_LEN(S) (((S) == NULL ? 0 : (S)->size))

GENERATE_ASDL_SEQ_CONSTRUCTOR(generic, void *);
GENERATE_ASDL_SEQ_CONSTRUCTOR(identifier, PyObject *);
GENERATE_ASDL_SEQ_CONSTRUCTOR(int, int);

// GENERATE_ASDL_SEQ_CONSTRUCTOR(mod, mod_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(stmt, stmt_ty)
GENERATE_ASDL_SEQ_CONSTRUCTOR(expr, expr_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(comprehension, comprehension_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(excepthandler, excepthandler_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(arguments, arguments_ty)
GENERATE_ASDL_SEQ_CONSTRUCTOR(arg, arg_ty)
GENERATE_ASDL_SEQ_CONSTRUCTOR(keyword, keyword_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(alias, alias_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(withitem, withitem_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(match_case, match_case_ty)
GENERATE_ASDL_SEQ_CONSTRUCTOR(pattern, pattern_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(type_ignore, type_ignore_ty)
// GENERATE_ASDL_SEQ_CONSTRUCTOR(type_param, type_param_ty)

static mod_ty _PyAST_Interactive(asdl_stmt_seq *body, PyArena *arena) {
  mod_ty p;
  p = (mod_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Interactive_kind;
  p->v.Interactive.body = body;
  return p;
}

static stmt_ty _PyAST_FunctionDef(identifier name, arguments_ty args,
                                  asdl_stmt_seq *body,
                                  asdl_expr_seq *decorator_list,
                                  expr_ty returns, string type_comment,
                                  asdl_type_param_seq *type_params, int lineno,
                                  int col_offset, int end_lineno,
                                  int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!name) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'name' is required for FunctionDef");
    return NULL;
  }
  if (!args) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'args' is required for FunctionDef");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = FunctionDef_kind;
  p->v.FunctionDef.name = name;
  p->v.FunctionDef.args = args;
  p->v.FunctionDef.body = body;
  p->v.FunctionDef.decorator_list = decorator_list;
  p->v.FunctionDef.returns = returns;
  p->v.FunctionDef.type_comment = type_comment;
  p->v.FunctionDef.type_params = type_params;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty
_PyAST_AsyncFunctionDef(identifier name, arguments_ty args, asdl_stmt_seq *body,
                        asdl_expr_seq *decorator_list, expr_ty returns,
                        string type_comment, asdl_type_param_seq *type_params,
                        int lineno, int col_offset, int end_lineno,
                        int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!name) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'name' is required for AsyncFunctionDef");
    return NULL;
  }
  if (!args) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'args' is required for AsyncFunctionDef");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = AsyncFunctionDef_kind;
  p->v.AsyncFunctionDef.name = name;
  p->v.AsyncFunctionDef.args = args;
  p->v.AsyncFunctionDef.body = body;
  p->v.AsyncFunctionDef.decorator_list = decorator_list;
  p->v.AsyncFunctionDef.returns = returns;
  p->v.AsyncFunctionDef.type_comment = type_comment;
  p->v.AsyncFunctionDef.type_params = type_params;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_ClassDef(identifier name, asdl_expr_seq *bases,
                               asdl_keyword_seq *keywords, asdl_stmt_seq *body,
                               asdl_expr_seq *decorator_list,
                               asdl_type_param_seq *type_params, int lineno,
                               int col_offset, int end_lineno,
                               int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!name) {
    PyErr_SetString(PyExc_ValueError, "field 'name' is required for ClassDef");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = ClassDef_kind;
  p->v.ClassDef.name = name;
  p->v.ClassDef.bases = bases;
  p->v.ClassDef.keywords = keywords;
  p->v.ClassDef.body = body;
  p->v.ClassDef.decorator_list = decorator_list;
  p->v.ClassDef.type_params = type_params;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Return(expr_ty value, int lineno, int col_offset,
                             int end_lineno, int end_col_offset,
                             PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Return_kind;
  p->v.Return.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Delete(asdl_expr_seq *targets, int lineno, int col_offset,
                             int end_lineno, int end_col_offset,
                             PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Delete_kind;
  p->v.Delete.targets = targets;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Assign(asdl_expr_seq *targets, expr_ty value,
                             string type_comment, int lineno, int col_offset,
                             int end_lineno, int end_col_offset,
                             PyArena *arena) {
  stmt_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError, "field 'value' is required for Assign");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Assign_kind;
  p->v.Assign.targets = targets;
  p->v.Assign.value = value;
  p->v.Assign.type_comment = type_comment;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_TypeAlias(expr_ty name, asdl_type_param_seq *type_params,
                                expr_ty value, int lineno, int col_offset,
                                int end_lineno, int end_col_offset,
                                PyArena *arena) {
  stmt_ty p;
  if (!name) {
    PyErr_SetString(PyExc_ValueError, "field 'name' is required for TypeAlias");
    return NULL;
  }
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for TypeAlias");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = TypeAlias_kind;
  p->v.TypeAlias.name = name;
  p->v.TypeAlias.type_params = type_params;
  p->v.TypeAlias.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_AugAssign(expr_ty target, operator_ty op, expr_ty value,
                                int lineno, int col_offset, int end_lineno,
                                int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!target) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'target' is required for AugAssign");
    return NULL;
  }
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "field 'op' is required for AugAssign");
    return NULL;
  }
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for AugAssign");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = AugAssign_kind;
  p->v.AugAssign.target = target;
  p->v.AugAssign.op = op;
  p->v.AugAssign.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_AnnAssign(expr_ty target, expr_ty annotation,
                                expr_ty value, int simple, int lineno,
                                int col_offset, int end_lineno,
                                int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!target) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'target' is required for AnnAssign");
    return NULL;
  }
  if (!annotation) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'annotation' is required for AnnAssign");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = AnnAssign_kind;
  p->v.AnnAssign.target = target;
  p->v.AnnAssign.annotation = annotation;
  p->v.AnnAssign.value = value;
  p->v.AnnAssign.simple = simple;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_For(expr_ty target, expr_ty iter, asdl_stmt_seq *body,
                          asdl_stmt_seq *orelse, string type_comment,
                          int lineno, int col_offset, int end_lineno,
                          int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!target) {
    PyErr_SetString(PyExc_ValueError, "field 'target' is required for For");
    return NULL;
  }
  if (!iter) {
    PyErr_SetString(PyExc_ValueError, "field 'iter' is required for For");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = For_kind;
  p->v.For.target = target;
  p->v.For.iter = iter;
  p->v.For.body = body;
  p->v.For.orelse = orelse;
  p->v.For.type_comment = type_comment;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_AsyncFor(expr_ty target, expr_ty iter,
                               asdl_stmt_seq *body, asdl_stmt_seq *orelse,
                               string type_comment, int lineno, int col_offset,
                               int end_lineno, int end_col_offset,
                               PyArena *arena) {
  stmt_ty p;
  if (!target) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'target' is required for AsyncFor");
    return NULL;
  }
  if (!iter) {
    PyErr_SetString(PyExc_ValueError, "field 'iter' is required for AsyncFor");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = AsyncFor_kind;
  p->v.AsyncFor.target = target;
  p->v.AsyncFor.iter = iter;
  p->v.AsyncFor.body = body;
  p->v.AsyncFor.orelse = orelse;
  p->v.AsyncFor.type_comment = type_comment;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_While(expr_ty test, asdl_stmt_seq *body,
                            asdl_stmt_seq *orelse, int lineno, int col_offset,
                            int end_lineno, int end_col_offset,
                            PyArena *arena) {
  stmt_ty p;
  if (!test) {
    PyErr_SetString(PyExc_ValueError, "field 'test' is required for While");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = While_kind;
  p->v.While.test = test;
  p->v.While.body = body;
  p->v.While.orelse = orelse;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_If(expr_ty test, asdl_stmt_seq *body,
                         asdl_stmt_seq *orelse, int lineno, int col_offset,
                         int end_lineno, int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!test) {
    PyErr_SetString(PyExc_ValueError, "field 'test' is required for If");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = If_kind;
  p->v.If.test = test;
  p->v.If.body = body;
  p->v.If.orelse = orelse;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_With(asdl_withitem_seq *items, asdl_stmt_seq *body,
                           string type_comment, int lineno, int col_offset,
                           int end_lineno, int end_col_offset, PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = With_kind;
  p->v.With.items = items;
  p->v.With.body = body;
  p->v.With.type_comment = type_comment;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_AsyncWith(asdl_withitem_seq *items, asdl_stmt_seq *body,
                                string type_comment, int lineno, int col_offset,
                                int end_lineno, int end_col_offset,
                                PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = AsyncWith_kind;
  p->v.AsyncWith.items = items;
  p->v.AsyncWith.body = body;
  p->v.AsyncWith.type_comment = type_comment;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Match(expr_ty subject, asdl_match_case_seq *cases,
                            int lineno, int col_offset, int end_lineno,
                            int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!subject) {
    PyErr_SetString(PyExc_ValueError, "field 'subject' is required for Match");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Match_kind;
  p->v.Match.subject = subject;
  p->v.Match.cases = cases;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Raise(expr_ty exc, expr_ty cause, int lineno,
                            int col_offset, int end_lineno, int end_col_offset,
                            PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Raise_kind;
  p->v.Raise.exc = exc;
  p->v.Raise.cause = cause;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Try(asdl_stmt_seq *body, asdl_excepthandler_seq *handlers,
                          asdl_stmt_seq *orelse, asdl_stmt_seq *finalbody,
                          int lineno, int col_offset, int end_lineno,
                          int end_col_offset, PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Try_kind;
  p->v.Try.body = body;
  p->v.Try.handlers = handlers;
  p->v.Try.orelse = orelse;
  p->v.Try.finalbody = finalbody;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_TryStar(asdl_stmt_seq *body,
                              asdl_excepthandler_seq *handlers,
                              asdl_stmt_seq *orelse, asdl_stmt_seq *finalbody,
                              int lineno, int col_offset, int end_lineno,
                              int end_col_offset, PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = TryStar_kind;
  p->v.TryStar.body = body;
  p->v.TryStar.handlers = handlers;
  p->v.TryStar.orelse = orelse;
  p->v.TryStar.finalbody = finalbody;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Assert(expr_ty test, expr_ty msg, int lineno,
                             int col_offset, int end_lineno, int end_col_offset,
                             PyArena *arena) {
  stmt_ty p;
  if (!test) {
    PyErr_SetString(PyExc_ValueError, "field 'test' is required for Assert");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Assert_kind;
  p->v.Assert.test = test;
  p->v.Assert.msg = msg;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Import(asdl_alias_seq *names, int lineno, int col_offset,
                             int end_lineno, int end_col_offset,
                             PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Import_kind;
  p->v.Import.names = names;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_ImportFrom(identifier module, asdl_alias_seq *names,
                                 int level, int lineno, int col_offset,
                                 int end_lineno, int end_col_offset,
                                 PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = ImportFrom_kind;
  p->v.ImportFrom.module = module;
  p->v.ImportFrom.names = names;
  p->v.ImportFrom.level = level;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Global(asdl_identifier_seq *names, int lineno,
                             int col_offset, int end_lineno, int end_col_offset,
                             PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Global_kind;
  p->v.Global.names = names;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Nonlocal(asdl_identifier_seq *names, int lineno,
                               int col_offset, int end_lineno,
                               int end_col_offset, PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Nonlocal_kind;
  p->v.Nonlocal.names = names;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Expr(expr_ty value, int lineno, int col_offset,
                           int end_lineno, int end_col_offset, PyArena *arena) {
  stmt_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError, "field 'value' is required for Expr");
    return NULL;
  }
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Expr_kind;
  p->v.Expr.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Pass(int lineno, int col_offset, int end_lineno,
                           int end_col_offset, PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Pass_kind;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Break(int lineno, int col_offset, int end_lineno,
                            int end_col_offset, PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Break_kind;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static stmt_ty _PyAST_Continue(int lineno, int col_offset, int end_lineno,
                               int end_col_offset, PyArena *arena) {
  stmt_ty p;
  p = (stmt_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Continue_kind;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_BoolOp(boolop_ty op, asdl_expr_seq *values, int lineno,
                             int col_offset, int end_lineno, int end_col_offset,
                             PyArena *arena) {
  expr_ty p;
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "field 'op' is required for BoolOp");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = BoolOp_kind;
  p->v.BoolOp.op = op;
  p->v.BoolOp.values = values;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_NamedExpr(expr_ty target, expr_ty value, int lineno,
                                int col_offset, int end_lineno,
                                int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!target) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'target' is required for NamedExpr");
    return NULL;
  }
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for NamedExpr");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = NamedExpr_kind;
  p->v.NamedExpr.target = target;
  p->v.NamedExpr.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_BinOp(expr_ty left, operator_ty op, expr_ty right,
                            int lineno, int col_offset, int end_lineno,
                            int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!left) {
    PyErr_SetString(PyExc_ValueError, "field 'left' is required for BinOp");
    return NULL;
  }
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "field 'op' is required for BinOp");
    return NULL;
  }
  if (!right) {
    PyErr_SetString(PyExc_ValueError, "field 'right' is required for BinOp");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = BinOp_kind;
  p->v.BinOp.left = left;
  p->v.BinOp.op = op;
  p->v.BinOp.right = right;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_UnaryOp(unaryop_ty op, expr_ty operand, int lineno,
                              int col_offset, int end_lineno,
                              int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!op) {
    PyErr_SetString(PyExc_ValueError, "field 'op' is required for UnaryOp");
    return NULL;
  }
  if (!operand) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'operand' is required for UnaryOp");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = UnaryOp_kind;
  p->v.UnaryOp.op = op;
  p->v.UnaryOp.operand = operand;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Lambda(arguments_ty args, expr_ty body, int lineno,
                             int col_offset, int end_lineno, int end_col_offset,
                             PyArena *arena) {
  expr_ty p;
  if (!args) {
    PyErr_SetString(PyExc_ValueError, "field 'args' is required for Lambda");
    return NULL;
  }
  if (!body) {
    PyErr_SetString(PyExc_ValueError, "field 'body' is required for Lambda");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Lambda_kind;
  p->v.Lambda.args = args;
  p->v.Lambda.body = body;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_IfExp(expr_ty test, expr_ty body, expr_ty orelse,
                            int lineno, int col_offset, int end_lineno,
                            int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!test) {
    PyErr_SetString(PyExc_ValueError, "field 'test' is required for IfExp");
    return NULL;
  }
  if (!body) {
    PyErr_SetString(PyExc_ValueError, "field 'body' is required for IfExp");
    return NULL;
  }
  if (!orelse) {
    PyErr_SetString(PyExc_ValueError, "field 'orelse' is required for IfExp");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = IfExp_kind;
  p->v.IfExp.test = test;
  p->v.IfExp.body = body;
  p->v.IfExp.orelse = orelse;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Dict(asdl_expr_seq *keys, asdl_expr_seq *values,
                           int lineno, int col_offset, int end_lineno,
                           int end_col_offset, PyArena *arena) {
  expr_ty p;
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Dict_kind;
  p->v.Dict.keys = keys;
  p->v.Dict.values = values;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Set(asdl_expr_seq *elts, int lineno, int col_offset,
                          int end_lineno, int end_col_offset, PyArena *arena) {
  expr_ty p;
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Set_kind;
  p->v.Set.elts = elts;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_ListComp(expr_ty elt, asdl_comprehension_seq *generators,
                               int lineno, int col_offset, int end_lineno,
                               int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!elt) {
    PyErr_SetString(PyExc_ValueError, "field 'elt' is required for ListComp");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = ListComp_kind;
  p->v.ListComp.elt = elt;
  p->v.ListComp.generators = generators;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_SetComp(expr_ty elt, asdl_comprehension_seq *generators,
                              int lineno, int col_offset, int end_lineno,
                              int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!elt) {
    PyErr_SetString(PyExc_ValueError, "field 'elt' is required for SetComp");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = SetComp_kind;
  p->v.SetComp.elt = elt;
  p->v.SetComp.generators = generators;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_DictComp(expr_ty key, expr_ty value,
                               asdl_comprehension_seq *generators, int lineno,
                               int col_offset, int end_lineno,
                               int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!key) {
    PyErr_SetString(PyExc_ValueError, "field 'key' is required for DictComp");
    return NULL;
  }
  if (!value) {
    PyErr_SetString(PyExc_ValueError, "field 'value' is required for DictComp");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = DictComp_kind;
  p->v.DictComp.key = key;
  p->v.DictComp.value = value;
  p->v.DictComp.generators = generators;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_GeneratorExp(expr_ty elt,
                                   asdl_comprehension_seq *generators,
                                   int lineno, int col_offset, int end_lineno,
                                   int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!elt) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'elt' is required for GeneratorExp");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = GeneratorExp_kind;
  p->v.GeneratorExp.elt = elt;
  p->v.GeneratorExp.generators = generators;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Await(expr_ty value, int lineno, int col_offset,
                            int end_lineno, int end_col_offset,
                            PyArena *arena) {
  expr_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError, "field 'value' is required for Await");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Await_kind;
  p->v.Await.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Yield(expr_ty value, int lineno, int col_offset,
                            int end_lineno, int end_col_offset,
                            PyArena *arena) {
  expr_ty p;
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Yield_kind;
  p->v.Yield.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_YieldFrom(expr_ty value, int lineno, int col_offset,
                                int end_lineno, int end_col_offset,
                                PyArena *arena) {
  expr_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for YieldFrom");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = YieldFrom_kind;
  p->v.YieldFrom.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Compare(expr_ty left, asdl_int_seq *ops,
                              asdl_expr_seq *comparators, int lineno,
                              int col_offset, int end_lineno,
                              int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!left) {
    PyErr_SetString(PyExc_ValueError, "field 'left' is required for Compare");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Compare_kind;
  p->v.Compare.left = left;
  p->v.Compare.ops = ops;
  p->v.Compare.comparators = comparators;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Call(expr_ty func, asdl_expr_seq *args,
                           asdl_keyword_seq *keywords, int lineno,
                           int col_offset, int end_lineno, int end_col_offset,
                           PyArena *arena) {
  expr_ty p;
  if (!func) {
    PyErr_SetString(PyExc_ValueError, "field 'func' is required for Call");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Call_kind;
  p->v.Call.func = func;
  p->v.Call.args = args;
  p->v.Call.keywords = keywords;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_FormattedValue(expr_ty value, int conversion,
                                     expr_ty format_spec, int lineno,
                                     int col_offset, int end_lineno,
                                     int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for FormattedValue");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = FormattedValue_kind;
  p->v.FormattedValue.value = value;
  p->v.FormattedValue.conversion = conversion;
  p->v.FormattedValue.format_spec = format_spec;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_JoinedStr(asdl_expr_seq *values, int lineno,
                                int col_offset, int end_lineno,
                                int end_col_offset, PyArena *arena) {
  expr_ty p;
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = JoinedStr_kind;
  p->v.JoinedStr.values = values;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Constant(constant value, string kind, int lineno,
                               int col_offset, int end_lineno,
                               int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError, "field 'value' is required for Constant");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Constant_kind;
  p->v.Constant.value = value;
  p->v.Constant.kind = kind;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Attribute(expr_ty value, identifier attr,
                                expr_context_ty ctx, int lineno, int col_offset,
                                int end_lineno, int end_col_offset,
                                PyArena *arena) {
  expr_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for Attribute");
    return NULL;
  }
  if (!attr) {
    PyErr_SetString(PyExc_ValueError, "field 'attr' is required for Attribute");
    return NULL;
  }
  if (!ctx) {
    PyErr_SetString(PyExc_ValueError, "field 'ctx' is required for Attribute");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Attribute_kind;
  p->v.Attribute.value = value;
  p->v.Attribute.attr = attr;
  p->v.Attribute.ctx = ctx;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Subscript(expr_ty value, expr_ty slice,
                                expr_context_ty ctx, int lineno, int col_offset,
                                int end_lineno, int end_col_offset,
                                PyArena *arena) {
  expr_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for Subscript");
    return NULL;
  }
  if (!slice) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'slice' is required for Subscript");
    return NULL;
  }
  if (!ctx) {
    PyErr_SetString(PyExc_ValueError, "field 'ctx' is required for Subscript");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Subscript_kind;
  p->v.Subscript.value = value;
  p->v.Subscript.slice = slice;
  p->v.Subscript.ctx = ctx;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Starred(expr_ty value, expr_context_ty ctx, int lineno,
                              int col_offset, int end_lineno,
                              int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError, "field 'value' is required for Starred");
    return NULL;
  }
  if (!ctx) {
    PyErr_SetString(PyExc_ValueError, "field 'ctx' is required for Starred");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Starred_kind;
  p->v.Starred.value = value;
  p->v.Starred.ctx = ctx;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Name(identifier id, expr_context_ty ctx, int lineno,
                           int col_offset, int end_lineno, int end_col_offset,
                           PyArena *arena) {
  expr_ty p;
  if (!id) {
    PyErr_SetString(PyExc_ValueError, "field 'id' is required for Name");
    return NULL;
  }
  if (!ctx) {
    PyErr_SetString(PyExc_ValueError, "field 'ctx' is required for Name");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Name_kind;
  p->v.Name.id = id;
  p->v.Name.ctx = ctx;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_List(asdl_expr_seq *elts, expr_context_ty ctx, int lineno,
                           int col_offset, int end_lineno, int end_col_offset,
                           PyArena *arena) {
  expr_ty p;
  if (!ctx) {
    PyErr_SetString(PyExc_ValueError, "field 'ctx' is required for List");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = List_kind;
  p->v.List.elts = elts;
  p->v.List.ctx = ctx;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Tuple(asdl_expr_seq *elts, expr_context_ty ctx,
                            int lineno, int col_offset, int end_lineno,
                            int end_col_offset, PyArena *arena) {
  expr_ty p;
  if (!ctx) {
    PyErr_SetString(PyExc_ValueError, "field 'ctx' is required for Tuple");
    return NULL;
  }
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Tuple_kind;
  p->v.Tuple.elts = elts;
  p->v.Tuple.ctx = ctx;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static expr_ty _PyAST_Slice(expr_ty lower, expr_ty upper, expr_ty step,
                            int lineno, int col_offset, int end_lineno,
                            int end_col_offset, PyArena *arena) {
  expr_ty p;
  p = (expr_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = Slice_kind;
  p->v.Slice.lower = lower;
  p->v.Slice.upper = upper;
  p->v.Slice.step = step;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static comprehension_ty _PyAST_comprehension(expr_ty target, expr_ty iter,
                                             asdl_expr_seq *ifs, int is_async,
                                             PyArena *arena) {
  comprehension_ty p;
  if (!target) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'target' is required for comprehension");
    return NULL;
  }
  if (!iter) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'iter' is required for comprehension");
    return NULL;
  }
  p = (comprehension_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->target = target;
  p->iter = iter;
  p->ifs = ifs;
  p->is_async = is_async;
  return p;
}

static excepthandler_ty _PyAST_ExceptHandler(expr_ty type, identifier name,
                                             asdl_stmt_seq *body, int lineno,
                                             int col_offset, int end_lineno,
                                             int end_col_offset,
                                             PyArena *arena) {
  excepthandler_ty p;
  p = (excepthandler_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = ExceptHandler_kind;
  p->v.ExceptHandler.type = type;
  p->v.ExceptHandler.name = name;
  p->v.ExceptHandler.body = body;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static arguments_ty _PyAST_arguments(asdl_arg_seq *posonlyargs,
                                     asdl_arg_seq *args, arg_ty vararg,
                                     asdl_arg_seq *kwonlyargs,
                                     asdl_expr_seq *kw_defaults, arg_ty kwarg,
                                     asdl_expr_seq *defaults, PyArena *arena) {
  arguments_ty p;
  p = (arguments_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->posonlyargs = posonlyargs;
  p->args = args;
  p->vararg = vararg;
  p->kwonlyargs = kwonlyargs;
  p->kw_defaults = kw_defaults;
  p->kwarg = kwarg;
  p->defaults = defaults;
  return p;
}

static arg_ty _PyAST_arg(identifier arg, expr_ty annotation,
                         string type_comment, int lineno, int col_offset,
                         int end_lineno, int end_col_offset, PyArena *arena) {
  arg_ty p;
  if (!arg) {
    PyErr_SetString(PyExc_ValueError, "field 'arg' is required for arg");
    return NULL;
  }
  p = (arg_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->arg = arg;
  p->annotation = annotation;
  p->type_comment = type_comment;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static keyword_ty _PyAST_keyword(identifier arg, expr_ty value, int lineno,
                                 int col_offset, int end_lineno,
                                 int end_col_offset, PyArena *arena) {
  keyword_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError, "field 'value' is required for keyword");
    return NULL;
  }
  p = (keyword_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->arg = arg;
  p->value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static alias_ty _PyAST_alias(identifier name, identifier asname, int lineno,
                             int col_offset, int end_lineno, int end_col_offset,
                             PyArena *arena) {
  alias_ty p;
  if (!name) {
    PyErr_SetString(PyExc_ValueError, "field 'name' is required for alias");
    return NULL;
  }
  p = (alias_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->name = name;
  p->asname = asname;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static withitem_ty _PyAST_withitem(expr_ty context_expr, expr_ty optional_vars,
                                   PyArena *arena) {
  withitem_ty p;
  if (!context_expr) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'context_expr' is required for withitem");
    return NULL;
  }
  p = (withitem_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->context_expr = context_expr;
  p->optional_vars = optional_vars;
  return p;
}

static match_case_ty _PyAST_match_case(pattern_ty pattern, expr_ty guard,
                                       asdl_stmt_seq *body, PyArena *arena) {
  match_case_ty p;
  if (!pattern) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'pattern' is required for match_case");
    return NULL;
  }
  p = (match_case_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->pattern = pattern;
  p->guard = guard;
  p->body = body;
  return p;
}

static pattern_ty _PyAST_MatchValue(expr_ty value, int lineno, int col_offset,
                                    int end_lineno, int end_col_offset,
                                    PyArena *arena) {
  pattern_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for MatchValue");
    return NULL;
  }
  p = (pattern_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = MatchValue_kind;
  p->v.MatchValue.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static pattern_ty _PyAST_MatchSingleton(constant value, int lineno,
                                        int col_offset, int end_lineno,
                                        int end_col_offset, PyArena *arena) {
  pattern_ty p;
  if (!value) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'value' is required for MatchSingleton");
    return NULL;
  }
  p = (pattern_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = MatchSingleton_kind;
  p->v.MatchSingleton.value = value;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static pattern_ty _PyAST_MatchSequence(asdl_pattern_seq *patterns, int lineno,
                                       int col_offset, int end_lineno,
                                       int end_col_offset, PyArena *arena) {
  pattern_ty p;
  p = (pattern_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = MatchSequence_kind;
  p->v.MatchSequence.patterns = patterns;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static pattern_ty _PyAST_MatchMapping(asdl_expr_seq *keys,
                                      asdl_pattern_seq *patterns,
                                      identifier rest, int lineno,
                                      int col_offset, int end_lineno,
                                      int end_col_offset, PyArena *arena) {
  pattern_ty p;
  p = (pattern_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = MatchMapping_kind;
  p->v.MatchMapping.keys = keys;
  p->v.MatchMapping.patterns = patterns;
  p->v.MatchMapping.rest = rest;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static pattern_ty _PyAST_MatchClass(expr_ty cls, asdl_pattern_seq *patterns,
                                    asdl_identifier_seq *kwd_attrs,
                                    asdl_pattern_seq *kwd_patterns, int lineno,
                                    int col_offset, int end_lineno,
                                    int end_col_offset, PyArena *arena) {
  pattern_ty p;
  if (!cls) {
    PyErr_SetString(PyExc_ValueError, "field 'cls' is required for MatchClass");
    return NULL;
  }
  p = (pattern_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = MatchClass_kind;
  p->v.MatchClass.cls = cls;
  p->v.MatchClass.patterns = patterns;
  p->v.MatchClass.kwd_attrs = kwd_attrs;
  p->v.MatchClass.kwd_patterns = kwd_patterns;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static pattern_ty _PyAST_MatchStar(identifier name, int lineno, int col_offset,
                                   int end_lineno, int end_col_offset,
                                   PyArena *arena) {
  pattern_ty p;
  p = (pattern_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = MatchStar_kind;
  p->v.MatchStar.name = name;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static pattern_ty _PyAST_MatchAs(pattern_ty pattern, identifier name,
                                 int lineno, int col_offset, int end_lineno,
                                 int end_col_offset, PyArena *arena) {
  pattern_ty p;
  p = (pattern_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = MatchAs_kind;
  p->v.MatchAs.pattern = pattern;
  p->v.MatchAs.name = name;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static pattern_ty _PyAST_MatchOr(asdl_pattern_seq *patterns, int lineno,
                                 int col_offset, int end_lineno,
                                 int end_col_offset, PyArena *arena) {
  pattern_ty p;
  p = (pattern_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = MatchOr_kind;
  p->v.MatchOr.patterns = patterns;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static type_param_ty _PyAST_TypeVar(identifier name, expr_ty bound, int lineno,
                                    int col_offset, int end_lineno,
                                    int end_col_offset, PyArena *arena) {
  type_param_ty p;
  if (!name) {
    PyErr_SetString(PyExc_ValueError, "field 'name' is required for TypeVar");
    return NULL;
  }
  p = (type_param_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = TypeVar_kind;
  p->v.TypeVar.name = name;
  p->v.TypeVar.bound = bound;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static type_param_ty _PyAST_ParamSpec(identifier name, int lineno,
                                      int col_offset, int end_lineno,
                                      int end_col_offset, PyArena *arena) {
  type_param_ty p;
  if (!name) {
    PyErr_SetString(PyExc_ValueError, "field 'name' is required for ParamSpec");
    return NULL;
  }
  p = (type_param_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = ParamSpec_kind;
  p->v.ParamSpec.name = name;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}

static type_param_ty _PyAST_TypeVarTuple(identifier name, int lineno,
                                         int col_offset, int end_lineno,
                                         int end_col_offset, PyArena *arena) {
  type_param_ty p;
  if (!name) {
    PyErr_SetString(PyExc_ValueError,
                    "field 'name' is required for TypeVarTuple");
    return NULL;
  }
  p = (type_param_ty)_PyArena_Malloc(arena, sizeof(*p));
  if (!p)
    return NULL;
  p->kind = TypeVarTuple_kind;
  p->v.TypeVarTuple.name = name;
  p->lineno = lineno;
  p->col_offset = col_offset;
  p->end_lineno = end_lineno;
  p->end_col_offset = end_col_offset;
  return p;
}
