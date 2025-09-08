"use client";

import * as React from "react";
import { LeadsTable } from "@/components/Table";
import { CSVUploader } from "@/components/CSVUploader";
import { Lead } from "@/components/types";
import { toast } from "sonner";
import Image from "next/image";

export default function Home() {
  return (
    <div className="font-sans items-center relative justify-items-center min-h-screen w-full">
      {/* <div className="[background-image:url('/noise.png')] -z-10 opacity-5 w-full h-full absolute top-0" /> */}
      <main className="flex flex-col h-max gap-18 p-20 py-5 justify-center items-center w-full max-w-full">
        <h1 className="relative z-20 ">
          <Image
            src={"/edin-logo.png"}
            width={300}
            height={150}
            alt="Edin logo"
          />
        </h1>
        <div className="w-full max-w-full flex flex-col items-start gap-2 overflow-x-auto">
          <LeadsTable />
        </div>
      </main>
    </div>
  );
}
