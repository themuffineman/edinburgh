import { createClient } from "@supabase/supabase-js";
import { NextRequest } from "next/server";

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
if (!supabaseUrl || !supabaseKey) {
  throw new Error("ENV variables missing");
}
const supabase = createClient(supabaseUrl, supabaseKey);

export async function POST(req: NextRequest) {
  try {
    console.log("received schedule req", new Date().toISOString());
    const body = await req.json();

    // Config
    const maxEmails = 20;
    const minGap = 70; // minutes
    const maxGap = 100; // minutes

    // Current UTC time
    const now = new Date();
    const nowUtc = new Date(
      Date.UTC(
        now.getUTCFullYear(),
        now.getUTCMonth(),
        now.getUTCDate(),
        now.getUTCHours(),
        now.getUTCMinutes(),
        now.getUTCSeconds()
      )
    );

    // UTC start and end of today
    const startOfDay = new Date(
      Date.UTC(
        nowUtc.getUTCFullYear(),
        nowUtc.getUTCMonth(),
        nowUtc.getUTCDate(),
        0,
        0,
        0
      )
    );
    const endOfDay = new Date(
      Date.UTC(
        nowUtc.getUTCFullYear(),
        nowUtc.getUTCMonth(),
        nowUtc.getUTCDate(),
        23,
        59,
        59
      )
    );

    // Fetch already scheduled emails for today
    const { data: scheduled, error: fetchError } = await supabase
      .from("scheduled-emails")
      .select("scheduled_time")
      .gte("scheduled_time", startOfDay.toISOString())
      .lte("scheduled_time", endOfDay.toISOString())
      .order("scheduled_time", { ascending: true });

    if (fetchError) throw new Error(fetchError.message);
    if (scheduled && scheduled.length >= maxEmails) {
      throw new Error("Max emails for today already scheduled");
    }

    // Calculate new email time with random gap (UTC)
    const gapMinutes =
      Math.floor(Math.random() * (maxGap - minGap + 1)) + minGap;
    let chosenTime: Date;

    if (!scheduled || scheduled.length === 0) {
      chosenTime = new Date(nowUtc.getTime() + gapMinutes * 60000);
    } else {
      const latest = new Date(scheduled[scheduled.length - 1].scheduled_time);
      chosenTime = new Date(latest.getTime() + gapMinutes * 60000);
    }

    // Stop if it goes past the end of the day
    if (chosenTime > endOfDay) {
      throw new Error("No valid time left today to schedule email");
    }

    // Insert into Supabase (ISO string = UTC)
    const { error: insertError, statusText } = await supabase
      .from("scheduled-emails")
      .insert({
        subject: body.subject,
        body_text: body.body_text,
        recipient: body.recipient,
        sender_name: "Petrus",
        scheduled_time: chosenTime.toISOString(),
      });

    if (insertError) throw new Error(insertError.message);

    return Response.json(
      {
        success: true,
        message: statusText,
        scheduled_time: chosenTime.toISOString(),
      },
      { status: 200 }
    );
  } catch (error: any) {
    console.error(error.message);
    return Response.json(
      { message: error.message, success: false },
      { status: 500 }
    );
  }
}
