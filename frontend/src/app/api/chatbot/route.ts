import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  try {
    // Verify authentication by checking for the authorization header
    const authHeader = req.headers.get('authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return NextResponse.json({ error: 'Authentication required' }, { status: 401 });
    }

    const token = authHeader.replace('Bearer ', '');
    const body = await req.json();
    const { message } = body;

    // Forward the request to the backend
    const backendResponse = await fetch('http://localhost:8000/api/chatbot', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`, // Forward the token to backend
      },
      body: JSON.stringify({ message }),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.text();
      return NextResponse.json(
        { error: `Backend error: ${errorData}` },
        { status: backendResponse.status }
      );
    }

    const responseData = await backendResponse.json();
    return NextResponse.json(responseData);
  } catch (error) {
    console.error('Chatbot API Error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}