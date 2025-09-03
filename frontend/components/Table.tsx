"use client";

import * as React from "react";
import {
  ColumnDef,
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
  VisibilityState,
} from "@tanstack/react-table";
import {
  ArrowUpDown,
  ChevronDown,
  MoreHorizontal,
  Mail,
  Trash2,
  User,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Lead, LeadsTableProps } from "./types";
import Link from "next/link";

// Simple dialog component since we don't have the UI dialog component
const SimpleDialog = ({
  isOpen,
  onClose,
  title,
  children,
}: {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      ></div>
      <div className="relative bg-white rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto z-50">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">{title}</h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              &times;
            </button>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
};

const SimpleTextarea = ({
  value,
  onChange,
  className,
}: {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  className?: string;
}) => {
  return (
    <textarea
      value={value}
      onChange={onChange}
      className={`border rounded-md p-2 w-full ${className || ""}`}
    />
  );
};

// Confirmation dialog component
const ConfirmDialog = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
}: {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="fixed inset-0 bg-black bg-opacity-50"
        onClick={onClose}
      ></div>
      <div className="relative bg-white rounded-lg shadow-lg max-w-md w-full z-50">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold">{title}</h3>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              &times;
            </button>
          </div>
          <p className="mb-6">{message}</p>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" onClick={onClose}>
              {cancelText}
            </Button>
            <Button
              onClick={() => {
                onConfirm();
                onClose();
              }}
            >
              {confirmText}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const columns: ColumnDef<Lead>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Name
          <ArrowUpDown />
        </Button>
      );
    },
    cell: ({ row }) => (
      <div className="capitalize trancate max-w-28">{row.getValue("name")}</div>
    ),
  },
  {
    accessorKey: "website",
    header: "Website",
    cell: ({ row }) => (
      <div className="lowercase max-w-28 truncate">
        <Link
          target="_blank"
          className="hover:underline"
          href={row.getValue("website")}
        >
          {row.getValue("website")}
        </Link>
      </div>
    ),
  },
  {
    accessorKey: "linkedin",
    header: "LinkedIn",
    cell: ({ row }) => (
      <div className="lowercase max-w-28 truncate">
        <Link
          target="_blank"
          className="hover:underline"
          href={row.getValue("linkedin")}
        >
          {row.getValue("linkedin")}
        </Link>
      </div>
    ),
  },
  {
    accessorKey: "emailAddress",
    header: "Email Address",
    cell: ({ row }) => (
      <div className="lowercase max-w-28 truncate">
        {row.getValue("emailAddress")}
      </div>
    ),
  },
  {
    accessorKey: "email",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Email
          <ArrowUpDown />
        </Button>
      );
    },
    cell: ({ row }) => (
      <div className="lowercase max-w-28 truncate">{row.getValue("email")}</div>
    ),
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const lead = row.original;
      const [isEmailDialogOpen, setIsEmailDialogOpen] = React.useState(false);
      const [isDeleteDialogOpen, setIsDeleteDialogOpen] = React.useState(false);
      const [isPersonalizeDialogOpen, setIsPersonalizeDialogOpen] =
        React.useState(false);
      const [emailBody, setEmailBody] = React.useState(
        "Hello " + lead.name + ",\n\nI hope this email finds you well..."
      );

      const handleSendEmail = () => {
        // Implement email sending logic here
        console.log("Sending email to:", lead.email);
        console.log("Email body:", emailBody);
        setIsEmailDialogOpen(false);
      };

      const handleDelete = () => {
        // Implement delete logic here
        console.log("Deleting lead:", lead.id);
      };

      const handlePersonalize = () => {
        // Implement personalize logic here
        console.log("Personalizing lead:", lead.id);
      };

      return (
        <div className="flex space-x-2">
          <Button
            className="cursor-pointer"
            variant="default"
            size="sm"
            onClick={() => setIsEmailDialogOpen(true)}
          >
            Send Email
            <Mail className="h-4 w-4" />
          </Button>
          <SimpleDialog
            isOpen={isEmailDialogOpen}
            onClose={() => setIsEmailDialogOpen(false)}
            title={`Send Email to ${lead.name}`}
          >
            <div className="mb-4">
              <p className="text-sm text-gray-500 mb-2">
                Edit the email content before sending to {lead.email}
              </p>
              <SimpleTextarea
                value={emailBody}
                onChange={(e) => setEmailBody(e.target.value)}
                className="min-h-[300px]"
              />
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                onClick={() => setIsEmailDialogOpen(false)}
              >
                Cancel
              </Button>
              <Button onClick={handleSendEmail}>Send Email</Button>
            </div>
          </SimpleDialog>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsPersonalizeDialogOpen(true)}
            className="cursor-pointer"
          >
            Personalize
            <User className="h-4 w-4" />
          </Button>
          <ConfirmDialog
            isOpen={isPersonalizeDialogOpen}
            onClose={() => setIsPersonalizeDialogOpen(false)}
            onConfirm={handlePersonalize}
            title="Personalize Lead"
            message={`Are you sure you want to personalize the lead "${lead.name}"?`}
          />
          <Button
            variant="destructive"
            size="sm"
            onClick={() => setIsDeleteDialogOpen(true)}
            className="cursor-pointer"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
          <ConfirmDialog
            isOpen={isDeleteDialogOpen}
            onClose={() => setIsDeleteDialogOpen(false)}
            onConfirm={handleDelete}
            title="Delete Lead"
            message={`Are you sure you want to delete the lead "${lead.name}"? This action cannot be undone.`}
            confirmText="Delete"
          />
        </div>
      );
    },
  },
];

export function LeadsTable({ leads }: LeadsTableProps) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  );
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});

  const table = useReactTable({
    data: leads,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  });

  return (
    <div className="w-full">
      <div className="flex items-center py-4">
        <Input
          placeholder="Filter emails..."
          value={(table.getColumn("email")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("email")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" className="ml-auto">
              Columns <ChevronDown />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {table
              .getAllColumns()
              .filter((column) => column.getCanHide())
              .map((column) => {
                return (
                  <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) =>
                      column.toggleVisibility(!!value)
                    }
                  >
                    {column.id}
                  </DropdownMenuCheckboxItem>
                );
              })}
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <div className="overflow-x-auto w-full rounded-md border">
        <Table className="w-full min-w-max">
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id} className="whitespace-nowrap">
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="whitespace-nowrap">
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="text-muted-foreground flex-1 text-sm">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
