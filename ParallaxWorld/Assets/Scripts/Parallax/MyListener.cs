using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;

public class MyListener : MonoBehaviour
{
    Thread thread;
    public int connectionPort = 25001;
    TcpListener server;
    TcpClient client;
    bool running;

    // Movement speed factor
    public float moveSpeed = 5f;

    // Camera offset for parallax effect
    public Vector3 cameraOffset = new Vector3(0, 0, -10);

    void Start()
    {
        // Receive on a separate thread so Unity doesn't freeze waiting for data
        ThreadStart ts = new ThreadStart(GetData);
        thread = new Thread(ts);
        thread.Start();
    }

    void GetData()
    {
        // Create the server
        server = new TcpListener(IPAddress.Any, connectionPort);
        server.Start();

        // Create a client to get the data stream
        client = server.AcceptTcpClient();

        // Start listening
        running = true;
        while (running)
        {
            Connection();
        }
        server.Stop();
    }

    void Connection()
    {
        // Read data from the network stream
        NetworkStream nwStream = client.GetStream();
        byte[] buffer = new byte[client.ReceiveBufferSize];
        int bytesRead = nwStream.Read(buffer, 0, client.ReceiveBufferSize);

        // Decode the bytes into a string
        string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead);

        // Make sure we're not getting an empty string
        if (!string.IsNullOrEmpty(dataReceived))
        {
            // Convert the received string of data to the format we are using
            position = ParseData(dataReceived);
            nwStream.Write(buffer, 0, bytesRead);
        }
    }

    // Parse X, Y, and Z from the received data
    public static Vector3 ParseData(string dataString)
    {
        Debug.Log(dataString);
        // Split the elements into an array
        string[] stringArray = dataString.Split(',');

        // Store as a Vector3, using Z for depth
        Vector3 result = new Vector3(
            float.Parse(stringArray[0]),  // X
            -float.Parse(stringArray[1]), // Invert Y
            float.Parse(stringArray[2]));  // Z

        return result;
    }

    // Position is the data being received in this example
    Vector3 position = Vector3.zero;

    void Update()
    {
        // Ensure cameraOffset is set correctly to match the desired depth
        Vector3 newPosition = new Vector3(position.x, -position.y, position.z); // Invert Y
        transform.position = Vector3.Lerp(transform.position, newPosition + cameraOffset, moveSpeed * Time.deltaTime);
        Debug.Log($"Current Position: {transform.position}");  // Debug print for current position
    }

}
