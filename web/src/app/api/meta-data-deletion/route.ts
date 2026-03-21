import { NextRequest, NextResponse } from "next/server";
import crypto from "crypto";

/**
 * Meta Data Deletion Callback Endpoint
 *
 * Meta sends a POST request here when a user removes Scribario from their
 * Facebook/Instagram account. We verify the signed_request, queue the deletion,
 * and return a confirmation code + status URL per Meta's requirements.
 *
 * See: https://developers.facebook.com/docs/development/create-an-app/app-dashboard/data-deletion-callback/
 */

const APP_SECRET = process.env.FACEBOOK_APP_SECRET || "";

interface ParsedSignedRequest {
  user_id: string;
  algorithm: string;
  issued_at: number;
}

function parseSignedRequest(
  signedRequest: string,
  secret: string
): ParsedSignedRequest | null {
  const [encodedSig, payload] = signedRequest.split(".", 2);
  if (!encodedSig || !payload) return null;

  // Decode signature
  const sig = Buffer.from(
    encodedSig.replace(/-/g, "+").replace(/_/g, "/"),
    "base64"
  );

  // Verify signature using HMAC-SHA256
  const expectedSig = crypto
    .createHmac("sha256", secret)
    .update(payload)
    .digest();

  if (!crypto.timingSafeEqual(sig, expectedSig)) return null;

  // Decode payload
  const decoded = Buffer.from(
    payload.replace(/-/g, "+").replace(/_/g, "/"),
    "base64"
  ).toString("utf-8");

  try {
    const data = JSON.parse(decoded);
    if (data.algorithm?.toUpperCase() !== "HMAC-SHA256") return null;
    return data as ParsedSignedRequest;
  } catch {
    return null;
  }
}

function generateConfirmationCode(): string {
  return crypto.randomBytes(16).toString("hex");
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const signedRequest = formData.get("signed_request");

    if (!signedRequest || typeof signedRequest !== "string") {
      return NextResponse.json(
        { error: "Missing signed_request" },
        { status: 400 }
      );
    }

    if (!APP_SECRET) {
      console.error("FACEBOOK_APP_SECRET not configured");
      return NextResponse.json(
        { error: "Server configuration error" },
        { status: 500 }
      );
    }

    const data = parseSignedRequest(signedRequest, APP_SECRET);
    if (!data) {
      return NextResponse.json(
        { error: "Invalid signed_request" },
        { status: 403 }
      );
    }

    const confirmationCode = generateConfirmationCode();
    const userId = data.user_id;

    // Log the deletion request — in production this would also:
    // 1. Look up tenant by Meta user_id
    // 2. Queue actual data deletion job
    // 3. Store the confirmation code for status lookup
    console.log(
      `[META DATA DELETION] User: ${userId}, Code: ${confirmationCode}`
    );

    // TODO: When Supabase JS client is available in web:
    // - Insert into a data_deletion_requests table
    // - Queue a worker job to delete user data
    // For now, log and return the required response format

    const statusUrl = `https://scribario.com/data-deletion-status?code=${confirmationCode}`;

    // Meta requires this exact response format
    return NextResponse.json({
      url: statusUrl,
      confirmation_code: confirmationCode,
    });
  } catch (error) {
    console.error("[META DATA DELETION] Error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
