"use client";

import * as React from "react";
import { LeadsTable } from "@/components/Table";
import { CSVUploader } from "@/components/CSVUploader";
import { Lead } from "@/components/types";

const sampleLeads: Lead[] = [
  {
    id: 1,
    name: "John Doe",
    website: "https://johndoe.com",
    linkedin: "https://linkedin.com/in/johndoe",
    emailAddress: "https://facebook.com/johndoe",
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
    email: {
      subject: "Hello Emily",
      body: "Hi Emily,\n\nI hope you're doing well! I wanted to reach out regarding...\n\nThanks,\nYour Name",
    },
  },
];

export default function Home() {
  return (
    <div className="font-sans items-center justify-items-center min-h-screen w-full">
      <main className="flex flex-col h-max gap-18 p-20 py-24 justify-center items-center w-full max-w-full">
        <h1 className="relative z-20 sm:text-6xl text-4xl ">
          <span className="bg-gradient-to-b from-neutral-200 to-neutral-500 bg-clip-text py-8 font-bold text-transparent ">
            Edinburgh
          </span>{" "}
          🕰️
        </h1>
        <div className="w-full max-w-full flex flex-col items-start gap-2 overflow-x-auto">
          <LeadsTable />
        </div>
      </main>
    </div>
  );
}
