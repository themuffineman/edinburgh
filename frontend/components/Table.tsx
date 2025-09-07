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
  CheckCircle2,
  ChevronDown,
  Loader2,
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

// Column definitions will be created inside the component to access action functions
const createColumns = (
  handleSendEmailClick: (leadData: Lead) => Promise<void>,
  handleDeleteClick: (leadData: Lead) => void,
  generateEmail: (leadData: Lead) => Promise<void>,
  updateEmail: (leadData: Lead) => void
): ColumnDef<Lead>[] => [
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
      const [emailSubject, setEmailSubject] = React.useState(
        lead.email.subject || ""
      );
      const [emailBody, setEmailBody] = React.useState(lead.email.body || "");

      // Reset local state when dialog opens/closes
      React.useEffect(() => {
        if (isEmailDialogOpen) {
          setEmailSubject(lead.email.subject || "");
          setEmailBody(lead.email.body || "");
        }
      }, [isEmailDialogOpen, lead.email.subject, lead.email.body]);

      const handleSaveEmail = () => {
        updateEmail({
          ...lead,
          email: {
            subject: emailSubject,
            body: emailBody,
          },
        });
        toast.success("Email saved successfully");
      };

      return (
        <div>
          <Dialog open={isEmailDialogOpen} onOpenChange={setIsEmailDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="min-w-[115px]" size="sm">
                View Email
                {lead.email.body && (
                  <CheckCircle2 className="size-4 stroke-green-500" />
                )}
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
                    onChange={(e) => {
                      setEmailSubject(e.target.value);
                    }}
                    value={emailSubject}
                    readOnly={!isEmailEditable}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Body</label>
                  <Textarea
                    onChange={(e) => {
                      setEmailBody(e.target.value);
                    }}
                    value={emailBody}
                    className="h-[300px] mt-1"
                    readOnly={!isEmailEditable}
                  />
                </div>
                {isEmailEditable && (
                  <div className="flex justify-end">
                    <Button onClick={handleSaveEmail} variant="default">
                      Save Changes
                    </Button>
                  </div>
                )}
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
      const [isGeneratingEmail, setIsGeneratingEmail] = React.useState(false);
      const [isSendingEmail, setisSendingEmail] = React.useState(false);
      return (
        <div className="flex space-x-2">
          <Button
            className="cursor-pointer"
            variant="default"
            disabled={!lead.email.body}
            size="sm"
            onClick={() => {
              setIsGeneratingEmail(true);
              handleSendEmailClick(lead).finally(() => {
                setisSendingEmail(false);
              });
            }}
          >
            Send Email
            {isSendingEmail ? (
              <Loader2 className="animate-spin size-4" />
            ) : (
              <Mail className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setIsGeneratingEmail(true);
              generateEmail(lead).finally(() => {
                setIsGeneratingEmail(false);
              });
            }}
            className="cursor-pointer relative"
          >
            Generate Email{" "}
            {!lead.email.body && (
              <span className="absolute -top-[2px] -right-[2px] border rounded-full size-[10px] bg-red-600 animate-pulse" />
            )}
            {isGeneratingEmail ? (
              <Loader2 className="animate-spin size-4" />
            ) : (
              <User className="h-4 w-4" />
            )}
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
  const [leads, setLeads] = React.useState<Lead[]>([]);

  const handleLeadsUpload = (newLeads: Lead[]) => {
    setLeads(newLeads);
  };
  const logData = async (lead: Lead) => {
    try {
      await request(`/api/crm`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(lead),
      });

      await request(`${process.env.ACTIVE_PIECES_URL}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company: lead.companyName,
          name: lead.name,
          title: lead.jobTitle,
          linkedin: lead.linkedin,
          website: lead.website,
          email: lead.email,
          time: new Date(),
        }),
      });
      toast.info("Lead data has been logged and tracked");
    } catch (error: any) {
      toast.info(`Logging and tracking failed -->${error.message} `);
    }
  };
  // Action functions with access to leads state
  const handleSendEmailClick = async (leadData: Lead) => {
    try {
      if (!SERVER_URL) {
        return;
      }
      toast.info("Sending email...");
      const leadAlreadyExists = await request(
        `/api/crm?email=${leadData.emailAddress}`
      );
      if (leadAlreadyExists.exists) {
        toast.error("We already contacted this lead");
        return;
      }
      const res = await fetch(`/api/send-email`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          subject: leadData.email.subject,
          body_text: leadData.email.body,
          recipient: leadData.emailAddress,
          sender_name: "Petrus",
        }),
      });
      if (res.ok) {
        toast.success("Email Scheduled Successfully");
        setLeads((prevLeads) =>
          prevLeads.filter((lead) => lead.id !== leadData.id)
        );
        await logData(leadData);
      } else {
        throw new Error("Failed to send email");
      }
    } catch (error: any) {
      toast.error(`Something went wrong❌: ${error.message}`, {
        duration: 5000,
      });
    }
  };

  const handleDeleteClick = (leadData: Lead) => {
    // Remove the lead from the leads array
    setLeads((prevLeads) =>
      prevLeads.filter((lead) => lead.id !== leadData.id)
    );
    toast.success("Lead deleted successfully");
  };

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
        toast.success("Email Successfully Generated✅");
        console.log(res);

        // Update the lead's email data with the generated email
        setLeads((prevLeads) =>
          prevLeads.map((lead) =>
            lead.id === leadData.id
              ? { ...lead, email: { subject: res.subject, body: res.body } }
              : lead
          )
        );
      } else {
        throw new Error("Email data undefined");
      }
    } catch (error: any) {
      toast.error(`Something went wrong --> ${error.message}`, {
        duration: 5000,
      });
    }
  };

  const updateEmail = (leadData: Lead) => {
    setLeads((prevLeads) =>
      prevLeads.map((lead) =>
        lead.id === leadData.id
          ? { ...lead, email: { ...lead.email, ...leadData.email } }
          : lead
      )
    );
  };

  // Create columns with access to action functions
  const columns = createColumns(
    handleSendEmailClick,
    handleDeleteClick,
    generateEmail,
    updateEmail
  );

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
