import { NextRequest, NextResponse } from 'next/server';

// Backend URL configuration
// Production deployments should set NEXT_PUBLIC_API_BASE_URL explicitly
const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Log warning if production without explicit configuration
if (process.env.NODE_ENV === 'production' && !process.env.NEXT_PUBLIC_API_BASE_URL) {
  console.warn('[LexGuard] NEXT_PUBLIC_API_BASE_URL not configured in production');
}

export async function GET(
  request: NextRequest,
  { params }: { params: { documentId: string } }
) {
  const documentId = params.documentId;

  try {
    const backendRes = await fetch(
      `${BACKEND_URL}/api/v1/documents/${encodeURIComponent(documentId)}/brief/export/pdf`,
      { method: 'GET', cache: 'no-store' }
    );

    if (!backendRes.ok) {
      return NextResponse.json(
        { error: 'PDF generation failed' },
        { status: backendRes.status }
      );
    }

    const pdfBuffer = await backendRes.arrayBuffer();

    return new NextResponse(pdfBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="LexGuard_Executive_Brief.pdf"',
        'Cache-Control': 'no-cache',
      },
    });
  } catch (err) {
    return NextResponse.json(
      { error: 'Export service unavailable' },
      { status: 502 }
    );
  }
}
