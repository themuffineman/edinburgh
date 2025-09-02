import { LeadsTable } from "@/components/Table";
import { Table } from "@/components/ui/table";
import Image from "next/image";
const sampleLeads = [
  {
    id: 1,
    name: "John Doe",
    website: "https://johndoe.com",
    linkedin: "https://linkedin.com/in/johndoe",
    facebook: "https://facebook.com/johndoe",
    email:
      "Hi John,\n\nI wanted to reach out and tell you about our services...\n\nBest,\nYour Name",
  },
  {
    id: 2,
    name: "Jane Smith",
    website: "https://janesmith.io",
    linkedin: "https://linkedin.com/in/janesmith",
    facebook: "https://facebook.com/janesmith",
    email:
      "Hello Jane,\n\nWe think our solution could help you achieve...\n\nCheers,\nYour Name",
  },
  {
    id: 3,
    name: "Mike Johnson",
    website: "https://mikejohnson.co",
    linkedin: "https://linkedin.com/in/mikejohnson",
    facebook: "https://facebook.com/mikejohnson",
    email:
      "Dear Mike,\n\nI wanted to share something that could be valuable to you...\n\nRegards,\nYour Name",
  },
  {
    id: 4,
    name: "Emily Davis",
    website: "https://emilydavis.net",
    linkedin: "https://linkedin.com/in/emilydavis",
    facebook: "https://facebook.com/emilydavis",
    email:
      "Hi Emily,\n\nI hope you're doing well! I wanted to reach out regarding...\n\nThanks,\nYour Name",
  },
];

export default function Home() {
  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 w-full">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start w-full max-w-full">
        <h1>Edinburgh</h1>
        <div className="w-full max-w-full overflow-x-auto">
          <LeadsTable leads={sampleLeads} />
        </div>
      </main>
    </div>
  );
}
