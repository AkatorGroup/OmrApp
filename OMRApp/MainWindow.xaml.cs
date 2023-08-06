using MessagingToolkit.Barcode;
using MessagingToolkit.QRCode.Codec;
using MessagingToolkit.QRCode.Codec.Data;
using Microsoft.Win32;
using Newtonsoft.Json;
using OMRApp.Classes;
using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;

namespace OMRApp
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private string imagePath;
        
        public MainWindow()
        {
            InitializeComponent();
        }

        private void UploadBtn_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "Image Files(*.PNG,*.JPG)|*.JPG;*.PNG";

            if (openFileDialog.ShowDialog() == true)
            {
                imagePath = openFileDialog.FileName;

                var button = (Button)sender;
                button.Content = "Uploaded...";
            }
            SheetImg.Source = new BitmapImage(new Uri(imagePath,UriKind.Absolute));
        }

        private async void GetResultBtn_Click(object sender, RoutedEventArgs e)
        {
            OptionsList.Items.Clear();
            if (string.IsNullOrEmpty(imagePath))
                return;

            Process process = new Process();
            process.StartInfo.FileName = "mark-recognation/run.exe";
            process.StartInfo.Arguments = $"--document {imagePath} --output output.json";
            process.StartInfo.UseShellExecute = false;
            process.StartInfo.CreateNoWindow = true;
            
            process.Start();
            await process.WaitForExitAsync();

            Sheet[] sheets = JsonConvert.DeserializeObject<Sheet[]>(File.ReadAllText("output.json"));

            foreach (var i in sheets)
            {
                SheetControl sheetControl = new SheetControl();

                sheetControl.NumberTxt.Text = i.Number.ToString();
                sheetControl.OptionTxt.Text = i.Option;
                OptionsList.Items.Add(sheetControl);
            }

            // Load the original image
            Bitmap originalImage = new Bitmap(imagePath); // Replace with the path to your image file

            // Define the region to cut
            System.Drawing.Rectangle cutRect = new System.Drawing.Rectangle(605, 770, 160, 160); // Replace with your desired rectangle dimensions

            // Create a new bitmap with the cut region
            Bitmap cutImage = new Bitmap(cutRect.Width, cutRect.Height);
            using (Graphics g = Graphics.FromImage(cutImage))
            {
                g.DrawImage(originalImage, new System.Drawing.Rectangle(0, 0, cutImage.Width, cutImage.Height), cutRect, GraphicsUnit.Pixel);
            }

            // Save the cut image to a file
            cutImage.Save("cut_image.jpg"); // Replace with the desired output file path

            // Dispose of the image objects


            Bitmap qrCodeImage = new Bitmap("cut_image.jpg"); // Replace with the path to your QR code image

            // Create a barcode reader instance
            QRCodeDecoder decoder = new QRCodeDecoder();
            string text = decoder.Decode(new QRCodeBitmapImage(qrCodeImage));
            QrCodeContentTxt.Text = $"QrCode content: {text}";

            //// Define the region to cut
            //cutRect = new System.Drawing.Rectangle(1510, 1350, 400, 270); // Replace with your desired rectangle dimensions

            //// Create a new bitmap with the cut region

            //cutImage = new Bitmap(cutRect.Width, cutRect.Height);
            //using (Graphics g = Graphics.FromImage(cutImage))
            //{
            //    g.DrawImage(originalImage, new System.Drawing.Rectangle(0, 0, cutImage.Width, cutImage.Height), cutRect, GraphicsUnit.Pixel);
            //}

            //// Save the cut image to a file
            //cutImage.Save("cut_image.gif"); // Replace with the desired output file path

            //// Dispose of the image objects
            //originalImage.Dispose();
            //cutImage.Dispose();

            //BarcodeDecoder barDecoder = new BarcodeDecoder();

            //Result result = barDecoder.Decode(new Bitmap("cut_image.gif"));

            //BarCodeContentTxt.Text = result.Text;


        }

    }
}
