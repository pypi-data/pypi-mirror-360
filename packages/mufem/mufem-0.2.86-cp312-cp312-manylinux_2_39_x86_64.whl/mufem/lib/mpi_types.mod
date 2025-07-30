!mod$ v1 sum:07f2498d341e8424
module mpi_types
type,bind(c)::mpi_status
integer(4)::mpi_source
integer(4)::mpi_tag
integer(4)::mpi_error
integer(4)::internal(1_8:3_8)
end type
type,bind(c)::mpi_comm
integer(4)::mpi_val
end type
type,bind(c)::mpi_datatype
integer(4)::mpi_val
end type
type,bind(c)::mpi_errhandler
integer(4)::mpi_val
end type
type,bind(c)::mpi_file
integer(4)::mpi_val
end type
type,bind(c)::mpi_group
integer(4)::mpi_val
end type
type,bind(c)::mpi_info
integer(4)::mpi_val
end type
type,bind(c)::mpi_message
integer(4)::mpi_val
end type
type,bind(c)::mpi_op
integer(4)::mpi_val
end type
type,bind(c)::mpi_request
integer(4)::mpi_val
end type
type,bind(c)::mpi_session
integer(4)::mpi_val
end type
type,bind(c)::mpi_win
integer(4)::mpi_val
end type
interface operator(.eq.)
procedure::ompi_comm_op_eq
procedure::ompi_datatype_op_eq
procedure::ompi_errhandler_op_eq
procedure::ompi_file_op_eq
procedure::ompi_group_op_eq
procedure::ompi_info_op_eq
procedure::ompi_message_op_eq
procedure::ompi_op_op_eq
procedure::ompi_request_op_eq
procedure::ompi_win_op_eq
end interface
interface operator(.ne.)
procedure::ompi_comm_op_ne
procedure::ompi_datatype_op_ne
procedure::ompi_errhandler_op_ne
procedure::ompi_file_op_ne
procedure::ompi_group_op_ne
procedure::ompi_info_op_ne
procedure::ompi_message_op_ne
procedure::ompi_op_op_ne
procedure::ompi_request_op_ne
procedure::ompi_win_op_ne
end interface
contains
function ompi_comm_op_eq(a,b)
type(mpi_comm),intent(in)::a
type(mpi_comm),intent(in)::b
logical(4)::ompi_comm_op_eq
end
function ompi_datatype_op_eq(a,b)
type(mpi_datatype),intent(in)::a
type(mpi_datatype),intent(in)::b
logical(4)::ompi_datatype_op_eq
end
function ompi_errhandler_op_eq(a,b)
type(mpi_errhandler),intent(in)::a
type(mpi_errhandler),intent(in)::b
logical(4)::ompi_errhandler_op_eq
end
function ompi_file_op_eq(a,b)
type(mpi_file),intent(in)::a
type(mpi_file),intent(in)::b
logical(4)::ompi_file_op_eq
end
function ompi_group_op_eq(a,b)
type(mpi_group),intent(in)::a
type(mpi_group),intent(in)::b
logical(4)::ompi_group_op_eq
end
function ompi_info_op_eq(a,b)
type(mpi_info),intent(in)::a
type(mpi_info),intent(in)::b
logical(4)::ompi_info_op_eq
end
function ompi_message_op_eq(a,b)
type(mpi_message),intent(in)::a
type(mpi_message),intent(in)::b
logical(4)::ompi_message_op_eq
end
function ompi_op_op_eq(a,b)
type(mpi_op),intent(in)::a
type(mpi_op),intent(in)::b
logical(4)::ompi_op_op_eq
end
function ompi_request_op_eq(a,b)
type(mpi_request),intent(in)::a
type(mpi_request),intent(in)::b
logical(4)::ompi_request_op_eq
end
function ompi_win_op_eq(a,b)
type(mpi_win),intent(in)::a
type(mpi_win),intent(in)::b
logical(4)::ompi_win_op_eq
end
function ompi_comm_op_ne(a,b)
type(mpi_comm),intent(in)::a
type(mpi_comm),intent(in)::b
logical(4)::ompi_comm_op_ne
end
function ompi_datatype_op_ne(a,b)
type(mpi_datatype),intent(in)::a
type(mpi_datatype),intent(in)::b
logical(4)::ompi_datatype_op_ne
end
function ompi_errhandler_op_ne(a,b)
type(mpi_errhandler),intent(in)::a
type(mpi_errhandler),intent(in)::b
logical(4)::ompi_errhandler_op_ne
end
function ompi_file_op_ne(a,b)
type(mpi_file),intent(in)::a
type(mpi_file),intent(in)::b
logical(4)::ompi_file_op_ne
end
function ompi_group_op_ne(a,b)
type(mpi_group),intent(in)::a
type(mpi_group),intent(in)::b
logical(4)::ompi_group_op_ne
end
function ompi_info_op_ne(a,b)
type(mpi_info),intent(in)::a
type(mpi_info),intent(in)::b
logical(4)::ompi_info_op_ne
end
function ompi_message_op_ne(a,b)
type(mpi_message),intent(in)::a
type(mpi_message),intent(in)::b
logical(4)::ompi_message_op_ne
end
function ompi_op_op_ne(a,b)
type(mpi_op),intent(in)::a
type(mpi_op),intent(in)::b
logical(4)::ompi_op_op_ne
end
function ompi_request_op_ne(a,b)
type(mpi_request),intent(in)::a
type(mpi_request),intent(in)::b
logical(4)::ompi_request_op_ne
end
function ompi_win_op_ne(a,b)
type(mpi_win),intent(in)::a
type(mpi_win),intent(in)::b
logical(4)::ompi_win_op_ne
end
end
