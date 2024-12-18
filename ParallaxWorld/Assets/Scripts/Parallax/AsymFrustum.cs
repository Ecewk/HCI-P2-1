﻿
/// <summary>
/// Asym frustum.
/// based on http://paulbourke.net/stereographics/stereorender/
/// and http://answers.unity3d.com/questions/165443/asymmetric-view-frusta-selective-region-rendering.html
/// </summary>
using UnityEngine;
using System.Collections;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;

[RequireComponent(typeof(Camera))]
[ExecuteInEditMode]
public class AsymFrustum : MonoBehaviour
{

    public GameObject virtualWindow;
    /// Screen/window to virtual world width (in units. I suggest using meters)
    public GameObject CameraHolder;
    public float width;
	/// Screen/window to virtual world height (in units. I suggest using meters)
    public float height;
	/// The maximum height the camera can have (up axis in local coordinates from  the virtualWindow) (in units. I suggest using meters)
    public float maxHeight = 2000.0f;
    float windowWidth;
    float windowHeight;
    Thread thread;
    public int connectionPort = 25001;
    TcpListener server;
    TcpClient client;
    bool running;
    Vector3 newPosition;
    bool positionUpdated = false;
    public bool verbose = false;
    public bool isInitialized = false;
    public Vector3 currentUserPos;
    public Vector3 lastUserPos;
    public Vector3 currentCameraPos;
    public Vector3 lastCameraPos;


    /// Called when this Component gets initialized
    void Start()
    {
        currentCameraPos = transform.position;
        lastCameraPos = currentCameraPos;
        //currentUserPos = Vector3.zero;
        //lastUserPos = currentUserPos;
        StartServer();
    }

    void StartServer()
    {
        thread = new Thread(new ThreadStart(ListenForClients));
        thread.IsBackground = true;
        thread.Start();
    }

    void ListenForClients()
    {
        server = new TcpListener(System.Net.IPAddress.Any, connectionPort);
        server.Start();
        running = true;

        while (running)
        {
            client = server.AcceptTcpClient();
            NetworkStream stream = client.GetStream();
            byte[] buffer = new byte[1024];
            int bytesRead;

            while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) != 0)
            {
                string data = System.Text.Encoding.ASCII.GetString(buffer, 0, bytesRead);
                Vector3 position = ParseData(data);
                lock(this)
                {
                    currentUserPos = position;
                    positionUpdated = true;
                }
            }
        }
    }

    Vector3 ParseData(string data)
    {
        string[] parts = data.Split(',');
        if (parts.Length == 3)
        {
            float x = float.Parse(parts[0]);
            float y = -float.Parse(parts[1]); //inverted y axis
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

    void UpdateCameraPosition(Vector3 position)
        {
            transform.position = position;
        }

    /// Late Update. Hopefully by now the head position got updated by whatever you use as input here.
    void LateUpdate()
    {
        windowWidth = width;
        windowHeight = height;
    // position changed
    if (positionUpdated && isInitialized)
    {
        lock (this)
        {
            Vector3 UserMovement = currentUserPos - lastUserPos;
            UserMovement *= 0.1f; // dampen the movement a bit
            currentCameraPos = lastCameraPos + UserMovement;
            transform.position = currentCameraPos; 

            lastUserPos = currentUserPos; 
            lastCameraPos = currentCameraPos;

            positionUpdated = false; 
        }
    }
        // gets the local position of this camera depending on the virtual screen
        Vector3 localPos = virtualWindow.transform.InverseTransformPoint(transform.position);

        setAsymmetricFrustum(GetComponent<Camera>(), localPos, GetComponent<Camera>().nearClipPlane);

    }
    /// <summary>
    /// Sets the asymmetric Frustum for the given virtual Window (at pos 0,0,0 )
    /// and the camera passed
    /// </summary>
    /// <param name="cam">Camera to get the asymmetric frustum for</param>
    /// <param name="pos">Position of the camera. Usually cam.transform.position</param>
    /// <param name="nearDist">Near clipping plane, usually cam.nearClipPlane</param>
    public void setAsymmetricFrustum(Camera cam, Vector3 pos, float nearDist)
    {

        // Focal length = orthogonal distance to image plane
        Vector3 newpos = pos;
        //newpos.Scale (new Vector3 (1, 1, 1));
        float focal = 1;

        newpos = new Vector3(newpos.x, newpos.z, newpos.y);
        if (verbose)
        {
            Debug.Log(newpos.x + ";" + newpos.y + ";" + newpos.z);
        }

        focal = Mathf.Clamp(newpos.z, 0.001f, maxHeight);

        // Ratio for intercept theorem
        float ratio = focal / nearDist;

        // Compute size for focal
        float imageLeft = (-windowWidth / 2.0f) - newpos.x;
        float imageRight = (windowWidth / 2.0f) - newpos.x;
        float imageTop = (windowHeight / 2.0f) - newpos.y;
        float imageBottom = (-windowHeight / 2.0f) - newpos.y;

        // Intercept theorem
        float nearLeft = imageLeft / ratio;
        float nearRight = imageRight / ratio;
        float nearTop = imageTop / ratio;
        float nearBottom = imageBottom / ratio;

        Matrix4x4 m = PerspectiveOffCenter(nearLeft, nearRight, nearBottom, nearTop, cam.nearClipPlane, cam.farClipPlane);
        cam.projectionMatrix = m;
    }



    /// <summary>
    /// Set an off-center projection, where perspective's vanishing
    /// point is not necessarily in the center of the screen.
    /// left/right/top/bottom define near plane size, i.e.
    /// how offset are corners of camera's near plane.
    /// Tweak the values and you can see camera's frustum change.
    /// </summary>
    /// <returns>The off center.</returns>
    /// <param name="left">Left.</param>
    /// <param name="right">Right.</param>
    /// <param name="bottom">Bottom.</param>
    /// <param name="top">Top.</param>
    /// <param name="near">Near.</param>
    /// <param name="far">Far.</param>
    Matrix4x4 PerspectiveOffCenter(float left, float right, float bottom, float top, float near, float far)
    {
        float x = (2.0f * near) / (right - left);
        float y = (2.0f * near) / (top - bottom);
        float a = (right + left) / (right - left);
        float b = (top + bottom) / (top - bottom);
        float c = -(far + near) / (far - near);
        float d = -(2.0f * far * near) / (far - near);
        float e = -1.0f;

        Matrix4x4 m = new Matrix4x4();
        m[0, 0] = x; m[0, 1] = 0; m[0, 2] = a; m[0, 3] = 0;
        m[1, 0] = 0; m[1, 1] = y; m[1, 2] = b; m[1, 3] = 0;
        m[2, 0] = 0; m[2, 1] = 0; m[2, 2] = c; m[2, 3] = d;
        m[3, 0] = 0; m[3, 1] = 0; m[3, 2] = e; m[3, 3] = 0;
        return m;
    }
    /// <summary>
    /// Draws gizmos in the Edit window.
    /// </summary>
    public virtual void OnDrawGizmos()
    {
        Gizmos.DrawLine(GetComponent<Camera>().transform.position, GetComponent<Camera>().transform.position + GetComponent<Camera>().transform.up * 10);
        Gizmos.color = Color.green;
        Gizmos.DrawLine(virtualWindow.transform.position, virtualWindow.transform.position + virtualWindow.transform.up);

        Gizmos.color = Color.blue;
        Gizmos.DrawLine(virtualWindow.transform.position - virtualWindow.transform.forward * 0.5f * windowHeight, virtualWindow.transform.position + virtualWindow.transform.forward * 0.5f * windowHeight);

        Gizmos.color = Color.red;
        Gizmos.DrawLine(virtualWindow.transform.position - virtualWindow.transform.right * 0.5f * windowWidth, virtualWindow.transform.position + virtualWindow.transform.right * 0.5f * windowWidth);
        Gizmos.color = Color.cyan;
        Vector3 leftBottom = virtualWindow.transform.position - virtualWindow.transform.right * 0.5f * windowWidth - virtualWindow.transform.forward * 0.5f * windowHeight;
        Vector3 leftTop = virtualWindow.transform.position - virtualWindow.transform.right * 0.5f * windowWidth + virtualWindow.transform.forward * 0.5f * windowHeight;
        Vector3 rightBottom = virtualWindow.transform.position + virtualWindow.transform.right * 0.5f * windowWidth - virtualWindow.transform.forward * 0.5f * windowHeight;
        Vector3 rightTop = virtualWindow.transform.position + virtualWindow.transform.right * 0.5f * windowWidth + virtualWindow.transform.forward * 0.5f * windowHeight;

        Gizmos.DrawLine(leftBottom, leftTop);
        Gizmos.DrawLine(leftTop, rightTop);
        Gizmos.DrawLine(rightTop, rightBottom);
        Gizmos.DrawLine(rightBottom, leftBottom);
        Gizmos.color = Color.grey;
        Gizmos.DrawLine(transform.position, leftTop);
        Gizmos.DrawLine(transform.position, rightTop);
        Gizmos.DrawLine(transform.position, rightBottom);
        Gizmos.DrawLine(transform.position, leftBottom);

    }
}