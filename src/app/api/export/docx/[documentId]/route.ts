import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: { documentId: string } }
) {
  const documentId = params.documentId;

  try {
    const backendRes = await fetch(
      `${BACKEND_URL}/api/v1/documents/${encodeURIComponent(documentId)}/brief/export/docx`,
      { method: 'GET', cache: 'no-store' }
    );

    if (!backendRes.ok) {
      return NextResponse.json(
        { error: 'DOCX generation failed' },
        { status: backendRes.status }
      );
    }

    const docxBuffer = await backendRes.arrayBuffer();

    return new NextResponse(docxBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'Content-Disposition': 'attachment; filename="LexGuard_Word_Checklist.docx"',
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
