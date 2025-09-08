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
    console.log("received schedule req", new Date());
    const body = await req.json();

    // Config
    const maxEmails = 20;
    const minGap = 70; // minutes
    const maxGap = 100; // minutes

    const now = new Date();
    const startOfDay = new Date(
      Date.UTC(
        now.getUTCFullYear(),
        now.getUTCMonth(),
        now.getUTCDate(),
        0,
        0,
        0
      )
    );
    const endOfDay = new Date(
      Date.UTC(
        now.getUTCFullYear(),
        now.getUTCMonth(),
        now.getUTCDate(),
        23,
        59,
        59
      )
    );

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

    // Decide new time
    let chosenTime: Date;

    const gapMinutes =
      Math.floor(Math.random() * (maxGap - minGap + 1)) + minGap;

    if (!scheduled || scheduled.length === 0) {
      chosenTime = new Date(now.getTime() + gapMinutes * 60000);
    } else {
      const latest = new Date(scheduled[scheduled.length - 1].scheduled_time);
      chosenTime = new Date(latest.getTime() + gapMinutes * 60000);
    }

    if (chosenTime > endOfDay) {
      throw new Error("No valid time left today to schedule email");
    }

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
      { success: true, message: statusText, scheduled_time: chosenTime },
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
