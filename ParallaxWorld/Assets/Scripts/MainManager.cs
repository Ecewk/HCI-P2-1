using System.Collections;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;
using UnityEngine.SceneManagement;

public class MainManager : MonoBehaviour
{

    Thread thread;
    public int port = 25001;
    private UdpClient udpServer;
    private IPEndPoint remoteEndPoint;
    bool positionUpdated = false;
    public bool isInitialized = false;
    public Vector3 currentUserPos;
    public Vector3 lastUserPos;
    public string SceneName = "";
    public GameObject target;
    public Camera cam;

    private static MainManager mainManager;
    // Start is called once before the first execution of Update after the MonoBehaviour is created
    void Start()
    {
        StartServer();
        Debug.Log($"TESTTTT");
    }

    void StartServer()
    {
        thread = new Thread(new ThreadStart(StartUDPServer));
        thread.IsBackground = true;
        thread.Start();
    }

    private void StartUDPServer()
    {
        udpServer = new UdpClient(port);
        remoteEndPoint = new IPEndPoint(IPAddress.Any, port);

        Debug.Log("Server started. Waiting for messages...");

        // Start receiving data asynchronously
        udpServer.BeginReceive(ReceiveData, null);
    }

    private void ReceiveData(IAsyncResult result)
    {
        byte[] receivedBytes = udpServer.EndReceive(result, ref remoteEndPoint);
        string receivedMessage = System.Text.Encoding.UTF8.GetString(receivedBytes);

        Debug.Log("Received from client: " + receivedMessage);

        // Process the received data
        if (receivedMessage.Contains(",")) {
            Vector3 position = ParseData(receivedMessage);
            //TODO check if this has to be removed
            lock(this)
            {
                currentUserPos = position;
                positionUpdated = true;
            }
        } else {
            SceneName = receivedMessage;
        }


        // Continue receiving data asynchronously
        udpServer.BeginReceive(ReceiveData, null);
    } 

    Vector3 ParseData(string data)
    {
        string[] parts = data.Split(',');
        if (parts.Length == 3)
        {
            float x = float.Parse(parts[0]);
            float y = float.Parse(parts[1]); //inverted y axis
            float z = float.Parse(parts[2]);

            if(!isInitialized)
            {
                currentUserPos = new Vector3(x, y, z);
                lastUserPos = currentUserPos;
                isInitialized = true;
                return currentUserPos;
            }
            return new Vector3(x, y, z);
        }
        return Vector3.zero;
    }

    void Awake()
    {
        if (mainManager == null) {
            mainManager = this;
            DontDestroyOnLoad(mainManager);
        }
        else {
            Destroy(gameObject);
        }
    } 

    // Update is called once per frame
    void Update()
    {
        if ((Input.GetKeyDown(KeyCode.W) || SceneName == "main") && (SceneManager.GetActiveScene().name == "FinalJungle" || SceneManager.GetActiveScene().name == "FinalWater")) {
            SceneManager.LoadScene("FinalMain");
            target.transform.position = new Vector3(1.49999976F,21.2399998F,49.7000008F);
        }
        if ((Input.GetKeyDown(KeyCode.A) || SceneName == "jungle") && (SceneManager.GetActiveScene().name == "FinalMain")) {
            SceneManager.LoadScene("FinalJungle");
            target.transform.position = new Vector3(-0.300000191F,24.5400028F,117F);
        }
        if ((Input.GetKeyDown(KeyCode.D) || SceneName == "water") && (SceneManager.GetActiveScene().name == "FinalMain")) {
            SceneManager.LoadScene("FinalWater");
            target.transform.position = new Vector3(23.810009F,14.1315308F,-66.5497284F);
        }

        float speed = 0.5F;
        //cam.transform.RotateAround(target.transform.position, cam.transform.right, -Input.GetAxis("Mouse Y") * speed);
        //cam.transform.RotateAround(target.transform.position, cam.transform.up, -Input.GetAxis("Mouse X") * speed);
        Debug.Log("Y     " + (currentUserPos.y - lastUserPos.y));
        Debug.Log("X   " + (currentUserPos.x - lastUserPos.x));
        cam.transform.RotateAround(target.transform.position, cam.transform.right, (currentUserPos.y - lastUserPos.y)/10 * speed);
        cam.transform.RotateAround(target.transform.position, cam.transform.up, -(currentUserPos.x - lastUserPos.x)/10 * speed);
        lastUserPos = currentUserPos; 
    }
}
