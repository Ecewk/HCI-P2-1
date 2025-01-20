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

    private float startTime;
    private string filePath = "sceneLoadTimes.txt";

    void Start()
    {
        StartServer();

        // Clear the file at the start (optional)
        System.IO.File.WriteAllText(filePath, "Scene Load Times:\n");

        // Subscribe to scene loaded event
        SceneManager.sceneLoaded += OnSceneLoaded;
    }

    void OnDestroy()
    {
        // Unsubscribe to avoid memory leaks
        SceneManager.sceneLoaded -= OnSceneLoaded;

        // Clean up the thread
        if (thread != null && thread.IsAlive)
        {
            thread.Abort();
        }
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
        string receivedMessage = Encoding.UTF8.GetString(receivedBytes);

        Debug.Log("Received from client: " + receivedMessage);

        if (receivedMessage.Contains(","))
        {
            Vector3 position = ParseData(receivedMessage);
            lock (this)
            {
                currentUserPos = position;
                positionUpdated = true;
            }
        }
        else
        {
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
            float y = float.Parse(parts[1]);
            float z = float.Parse(parts[2]);

            if (!isInitialized)
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
        if (mainManager == null)
        {
            mainManager = this;
            DontDestroyOnLoad(mainManager);
        }
        else
        {
            Destroy(gameObject);
        }
    }

    void Update()
    {
        if ((Input.GetKeyDown(KeyCode.W) || SceneName == "main") && (SceneManager.GetActiveScene().name == "FinalJungle" || SceneManager.GetActiveScene().name == "FinalWater"))
        {
            LoadSceneWithTiming("FinalMain", new Vector3(1.49999976F, 21.2399998F, 49.7000008F));
        }
        if ((Input.GetKeyDown(KeyCode.A) || SceneName == "jungle") && (SceneManager.GetActiveScene().name == "FinalMain"))
        {
            LoadSceneWithTiming("FinalJungle", new Vector3(-0.300000191F, 24.5400028F, 117F));
        }
        if ((Input.GetKeyDown(KeyCode.D) || SceneName == "water") && (SceneManager.GetActiveScene().name == "FinalMain"))
        {
            LoadSceneWithTiming("FinalWater", new Vector3(-0.300000191F, 13.7399998F, 87.6999969F));
        }

        float speed = 0.5F;
        cam.transform.RotateAround(target.transform.position, cam.transform.right, (currentUserPos.y - lastUserPos.y) / 10 * speed);
        cam.transform.RotateAround(target.transform.position, cam.transform.up, -(currentUserPos.x - lastUserPos.x) / 10 * speed);
        lastUserPos = currentUserPos;
    }

    private void LoadSceneWithTiming(string sceneName, Vector3 targetPosition)
    {
        startTime = Time.realtimeSinceStartup;
        SceneManager.LoadScene(sceneName);
        target.transform.position = targetPosition;
    }

    private void OnSceneLoaded(Scene scene, LoadSceneMode mode)
    {
        float loadTime = Time.realtimeSinceStartup - startTime;
        Debug.Log($"Scene '{scene.name}' loaded in {loadTime} seconds.");
        SaveLoadTime(scene.name, loadTime);
    }

    private void SaveLoadTime(string sceneName, float loadTime)
    {
        string logEntry = $"Scene '{sceneName}' loaded in {loadTime:F2} seconds.\n";
        System.IO.File.AppendAllText(filePath, logEntry);
    }
}
