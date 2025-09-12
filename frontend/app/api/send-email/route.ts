import { createClient } from "@supabase/supabase-js";
import { NextRequest } from "next/server";

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_KEY;
if (!supabaseUrl || !supabaseKey) {
  throw new Error("ENV variables missing");
}
const supabase = createClient(supabaseUrl, supabaseKey);

const emailInboxes = [
  "petrus@pendoratech.com",
  "petrussheya@pendoratech.com",
  "peter@pendoratech.com",
] as const;
export async function POST(req: NextRequest) {
  try {
    console.log("received schedule req", new Date().toISOString());
    const body = await req.json();

    // Config
    const maxEmailsPerInbox = 10;
    const maxEmailsTotal = 30; // 3 inboxes * 10 emails/inbox
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

    // Fetch already scheduled emails for today, grouped by mailbox
    const { data: scheduled, error: fetchError } = await supabase
      .from("scheduled-emails")
      .select("scheduled_time, mailbox")
      .gte("scheduled_time", startOfDay.toISOString())
      .lte("scheduled_time", endOfDay.toISOString())
      .order("scheduled_time", { ascending: true });

    if (fetchError) throw new Error(fetchError.message);

    // Check total emails scheduled
    if (scheduled && scheduled.length >= maxEmailsTotal) {
      throw new Error("Max emails for today already scheduled");
    }

    // Count emails per inbox
    const inboxCounts = new Map<string, number>();
    const latestTimePerInbox = new Map<string, Date>();
    emailInboxes.forEach((inbox) => inboxCounts.set(inbox, 0));

    if (scheduled) {
      scheduled.forEach((email) => {
        const count = inboxCounts.get(email.mailbox) || 0;
        inboxCounts.set(email.mailbox, count + 1);
        const latest = latestTimePerInbox.get(email.mailbox);
        const emailTime = new Date(email.scheduled_time);
        if (!latest || emailTime > latest) {
          latestTimePerInbox.set(email.mailbox, emailTime);
        }
      });
    }

    // Find an available inbox
    let availableInbox: string | undefined;
    for (const inbox of emailInboxes) {
      if ((inboxCounts.get(inbox) || 0) < maxEmailsPerInbox) {
        availableInbox = inbox;
        break;
      }
    }

    if (!availableInbox) {
      throw new Error("All inboxes have reached their daily email limit.");
    }

    // Calculate new email time with random gap (UTC)
    const gapMinutes =
      Math.floor(Math.random() * (maxGap - minGap + 1)) + minGap;
    let chosenTime: Date;

    const latestForInbox = latestTimePerInbox.get(availableInbox);
    if (!latestForInbox) {
      // First email for this inbox today
      chosenTime = new Date(nowUtc.getTime() + gapMinutes * 60000);
    } else {
      // Schedule after the last email for this specific inbox
      chosenTime = new Date(latestForInbox.getTime() + gapMinutes * 60000);
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
        mailbox: availableInbox, // Assign the selected mailbox
      });

    if (insertError) throw new Error(insertError.message);

    return Response.json(
      {
        success: true,
        message: statusText,
        scheduled_time: chosenTime.toISOString(),
        assigned_mailbox: availableInbox,
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
