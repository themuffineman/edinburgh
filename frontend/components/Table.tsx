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
import { ArrowUpDown, ChevronDown, Mail, Trash2, User } from "lucide-react";

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
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
import { Switch } from "./ui/switch";
import { CSVUploader } from "./CSVUploader";
import { request } from "@/lib/utils";
import { toast } from "sonner";
const SERVER_URL = process.env.NEXT_PUBLIC_SERVER_URL;
type ServerEmailResponse = {
  body: string;
  subject: string;
};
const sampleLeads: Lead[] = [
  {
    id: 1,
    name: "Lou Aleman",
    website: "http://www.coloradoseoservices.net",
    linkedin: "http://www.linkedin.com/in/lou-aleman-79514910",
    emailAddress: "lou@coloradoseoservices.net",
    companyName: "Colorado SEO Services",
    jobTitle: "Founder & CEO",
    email: {
      subject: "Hello John",
      body: "Hi John,\n\nI wanted to reach out and tell you about our services...\n\nBest,\nYour Name",
    },
  },
  {
    id: 2,
    name: "Jane Smith",
    website: "https://janesmith.io",
    linkedin: "https://linkedin.com/in/janesmith",
    emailAddress: "https://facebook.com/janesmith",
    companyName: "ACME Inc",
    jobTitle: "Founder & CEO",
    email: {
      subject: "Hello Jane",
      body: "Hello Jane,\n\nWe think our solution could help you achieve...\n\nCheers,\nYour Name",
    },
  },
  {
    id: 3,
    name: "Mike Johnson",
    website: "https://mikejohnson.co",
    linkedin: "https://linkedin.com/in/mikejohnson",
    emailAddress: "https://facebook.com/mikejohnson",
    companyName: "ACME Inc",
    jobTitle: "Founder & CEO",
    email: {
      subject: "Hello Mike",
      body: "Dear Mike,\n\nI wanted to share something that could be valuable to you...\n\nRegards,\nYour Name",
    },
  },
  {
    id: 4,
    name: "Emily Davis",
    website: "https://emilydavis.net",
    linkedin: "https://linkedin.com/in/emilydavis",
    emailAddress: "https://facebook.com/emilydavis",
    companyName: "ACME Inc",
    jobTitle: "Founder & CEO",
    email: {
      subject: "Hello Emily",
      body: "Hi Emily,\n\nI hope you're doing well! I wanted to reach out regarding...\n\nThanks,\nYour Name",
    },
  },
];
// Simple onclick functions that take row data as parameters
const handleSendEmailClick = async (leadData: Lead) => {
  try {
    if (!SERVER_URL) {
      return;
    }
    toast.info("Sending email...");
    const res = await fetch(`${SERVER_URL}/send-email`, {
      method: "POST",
      body: JSON.stringify({
        subject: leadData.email.subject,
        body: leadData.email.body,
      }),
    });
    if (res.ok) {
      toast.success("Email Successully Sent");
    } else {
      throw new Error("Email data undefined");
    }
  } catch (error: any) {
    toast.error(`Something went wrong❌: , ${error.message}`, {
      duration: 5000,
    });
  }
};

const handleDeleteClick = (leadData: Lead) => {};

const generateEmail = async (leadData: Lead) => {
  try {
    if (!SERVER_URL) {
      return;
    }
    toast.info("Generating email...");
    const res: ServerEmailResponse = await request(
      `${SERVER_URL}/generate-email`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company_name: leadData.companyName,
          decision_maker_name: leadData.name,
          decision_maker_title: leadData.jobTitle,
          linkedin_url: leadData.linkedin,
          website_url: leadData.website,
        }),
      }
    );
    if (res) {
      toast.success("Email Successully Generated✅");
      console.log(res);
      return res;
    } else {
      throw new Error("Email data undefined");
    }
  } catch (error: any) {
    toast.error(`Something went wrong --> ${error.message}`, {
      duration: 5000,
    });
  }
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
      <div className="capitalize truncate max-w-28 ">
        {row.getValue("name")}
      </div>
    ),
  },
  {
    accessorKey: "jobTitle",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Job Title
          <ArrowUpDown />
        </Button>
      );
    },
    cell: ({ row }) => (
      <div className="capitalize truncate max-w-28">
        {row.getValue("jobTitle")}
      </div>
    ),
  },
  {
    accessorKey: "companyName",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
        >
          Company Name
          <ArrowUpDown />
        </Button>
      );
    },
    cell: ({ row }) => (
      <div className="capitalize truncate max-w-28">
        {row.getValue("companyName")}
      </div>
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
    cell: ({ row }) => {
      const lead = row.original;
      const [isEmailDialogOpen, setIsEmailDialogOpen] = React.useState(false);
      const [isEmailEditable, setIsEmailEditable] = React.useState(false);

      return (
        <div>
          <Dialog open={isEmailDialogOpen} onOpenChange={setIsEmailDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                View Email
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Email Preview for {lead.name}</DialogTitle>
                <div className="flex rounded-md flex-row items-center text-sm mt-3 border shadow p-2 w-max font-semibold gap-4">
                  <p>Edit Email </p>
                  <Switch
                    checked={isEmailEditable}
                    onCheckedChange={(bool) => {
                      setIsEmailEditable(bool);
                    }}
                  />
                </div>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Subject</label>
                  <Input
                    defaultValue={lead.email.subject}
                    readOnly={!isEmailEditable}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Body</label>
                  <Textarea
                    defaultValue={lead.email.body}
                    className="min-h-[300px] mt-1"
                    readOnly={!isEmailEditable}
                  />
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      );
    },
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const lead = row.original;

      return (
        <div className="flex space-x-2">
          <Button
            className="cursor-pointer"
            variant="default"
            size="sm"
            onClick={() => {
              const res = handleSendEmailClick(lead);
            }}
          >
            Send Email
            <Mail className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => generateEmail(lead)}
            className="cursor-pointer"
          >
            Generate Email
            <User className="h-4 w-4" />
          </Button>
          <Button
            variant="destructive"
            size="sm"
            onClick={() => handleDeleteClick(lead)}
            className="cursor-pointer"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      );
    },
  },
];

export function LeadsTable() {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  );
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({});
  const [rowSelection, setRowSelection] = React.useState({});
  const [leads, setLeads] = React.useState<Lead[]>(sampleLeads);

  const handleLeadsUpload = (newLeads: Lead[]) => {
    setLeads(newLeads);
  };

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
        <div className="flex items-center gap-2 ml-auto">
          <CSVUploader onLeadsUpload={handleLeadsUpload} />
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
        <div className="font-bold">
          Page {table.getState().pagination.pageIndex + 1} of{" "}
          {table.getPageCount()}
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
