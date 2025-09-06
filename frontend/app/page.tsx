"use client";

import * as React from "react";
import { LeadsTable } from "@/components/Table";
import { CSVUploader } from "@/components/CSVUploader";
import { Lead } from "@/components/types";
import { toast } from "sonner";

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
